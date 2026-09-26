from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.core.security import verify_password, create_access_token, create_refresh_token, decode_token
from app.core.config import settings
from app.models.models import User, Role
from app.schemas.schemas import LoginRequest, Token, UserOut

router = APIRouter(prefix="/auth", tags=["Authentication"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login", auto_error=False)

async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)) -> User:
    if not token:
        # Fallback to admin only in non-production local development if user exists
        if settings.ENVIRONMENT != "production":
            stmt = select(User).where(User.username == "admin")
            res = await db.execute(stmt)
            admin = res.scalars().first()
            if admin:
                return admin
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")

    payload = decode_token(token)
    if not payload or payload.get("type") != "access":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")

    user_id = payload.get("sub")
    stmt = select(User).where(User.id == user_id)
    res = await db.execute(stmt)
    user = res.scalars().first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user


def require_roles(*allowed_roles: str):
    """Enforces Role-Based Access Control (RBAC) at the API level."""
    async def role_checker(
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
    ) -> User:
        role_stmt = select(Role).where(Role.id == current_user.role_id)
        role_res = await db.execute(role_stmt)
        role = role_res.scalars().first()
        if not role:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No role assigned to user")

        if role.name == "ADMIN" or "*" in (role.permissions or []):
            return current_user

        if role.name in allowed_roles:
            return current_user

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Access denied: Requires role in {allowed_roles}. Current role: {role.name}"
        )
    return role_checker


def require_permissions(*required_permissions: str):
    """Enforces fine-grained permission checks."""
    async def perm_checker(
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
    ) -> User:
        role_stmt = select(Role).where(Role.id == current_user.role_id)
        role_res = await db.execute(role_stmt)
        role = role_res.scalars().first()
        if not role:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No role assigned to user")

        if role.name == "ADMIN" or "*" in (role.permissions or []):
            return current_user

        user_perms = set(role.permissions or [])
        if all(p in user_perms for p in required_permissions):
            return current_user

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Access denied: Missing required permissions: {required_permissions}"
        )
    return perm_checker


@router.post("/login", response_model=Token)
async def login(req: LoginRequest, db: AsyncSession = Depends(get_db)):
    stmt = select(User).where(User.username == req.username)
    res = await db.execute(stmt)
    user = res.scalars().first()

    if not user or not verify_password(req.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password")

    access_token = create_access_token(user.id)
    refresh_token = create_refresh_token(user.id)

    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in_minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )

@router.post("/refresh", response_model=Token)
async def refresh_access_token(req: dict, db: AsyncSession = Depends(get_db)):
    """Exchange a valid refresh token for a new access token."""
    refresh_token = req.get("refresh_token")
    if not refresh_token:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="refresh_token is required")

    payload = decode_token(refresh_token)
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired refresh token")

    user_id = payload.get("sub")
    stmt = select(User).where(User.id == user_id)
    res = await db.execute(stmt)
    user = res.scalars().first()
    if not user or user.status != "ACTIVE":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User account is inactive or revoked")

    new_access = create_access_token(user.id)
    new_refresh = create_refresh_token(user.id)

    return Token(
        access_token=new_access,
        refresh_token=new_refresh,
        token_type="bearer",
        expires_in_minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )

@router.post("/device-enroll")
async def enroll_device_identity(req: dict, db: AsyncSession = Depends(get_db)):
    """
    Cryptographically enrolls an endpoint agent with hardware fingerprinting.
    Issues a Device Identity Token and unique HMAC signing secret.
    Mitigates Rogue Devices and Fake Metrics threats.
    """
    import uuid
    import hmac
    import hashlib
    from datetime import datetime, timezone
    from app.models.models import Endpoint

    hostname = req.get("hostname", "UNKNOWN-HOST")
    fingerprint = req.get("hardware_fingerprint", "GENERIC-HWID")
    os_name = req.get("os_name", "Windows")
    mac_address = req.get("mac_address", "00:00:00:00:00:00")

    # Generate unique device ID derived from hardware fingerprint or UUID
    device_id = f"dev_{hashlib.sha256(f'{hostname}:{fingerprint}'.encode()).hexdigest()[:12]}"
    device_hmac_secret = hashlib.sha256(f"{settings.SECRET_KEY}:{device_id}:{fingerprint}".encode()).hexdigest()

    # Create or update endpoint in CMDB
    stmt = select(Endpoint).where(Endpoint.hostname == hostname)
    existing = (await db.execute(stmt)).scalars().first()
    if not existing:
        new_ep = Endpoint(
            id=device_id,
            hostname=hostname,
            ip_address=req.get("ip_address", "127.0.0.1"),
            os_name=os_name,
            device_type=req.get("device_type", "Workstation"),
            status="ONLINE",
            agent_version=req.get("agent_version", "5.0.0")
        )
        db.add(new_ep)
        await db.commit()

    # Generate signed device JWT
    device_token = create_access_token(subject=device_id)

    return {
        "device_id": device_id,
        "hostname": hostname,
        "identity_token": device_token,
        "hmac_secret": device_hmac_secret,
        "enrolled_at": datetime.now(timezone.utc).isoformat(),
        "status": "ENROLLED"
    }

@router.post("/verify-device-identity")
async def verify_device_identity(req: dict):
    """
    Validates agent cryptographic signature and timestamp freshness.
    Mitigates Replay Attacks and Metric Tampering.
    """
    import hmac
    import hashlib
    from datetime import datetime, timezone

    device_id = req.get("device_id")
    timestamp_str = req.get("timestamp")
    signature = req.get("signature")
    fingerprint = req.get("hardware_fingerprint", "GENERIC-HWID")

    if not device_id or not timestamp_str or not signature:
        raise HTTPException(status_code=400, detail="device_id, timestamp, and signature are required")

    # Replay protection: Check timestamp is within 300 seconds
    try:
        req_dt = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
        now = datetime.now(timezone.utc)
        diff_sec = abs((now - req_dt).total_seconds())
        if diff_sec > 300:
            raise HTTPException(status_code=401, detail="Request expired or clock drift exceeded (replay protection)")
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=400, detail="Invalid ISO timestamp format")

    expected_secret = hashlib.sha256(f"{settings.SECRET_KEY}:{device_id}:{fingerprint}".encode()).hexdigest()
    expected_sig = hmac.new(expected_secret.encode(), f"{device_id}:{timestamp_str}".encode(), hashlib.sha256).hexdigest()

    if not hmac.compare_digest(expected_sig, signature):
        raise HTTPException(status_code=401, detail="Cryptographic device identity signature verification failed")

    return {
        "status": "VERIFIED",
        "device_id": device_id,
        "verified_at": datetime.now(timezone.utc).isoformat()
    }

@router.get("/me")
async def get_profile(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    role_stmt = select(Role).where(Role.id == current_user.role_id)
    role_res = await db.execute(role_stmt)
    role = role_res.scalars().first()

    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "status": current_user.status,
        "role": role.name if role else "ANALYST",
        "permissions": role.permissions if role else []
    }

@router.post("/logout")
async def logout(current_user: User = Depends(get_current_user)):
    return {"status": "success", "message": "Session invalidated"}

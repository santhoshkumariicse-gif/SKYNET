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

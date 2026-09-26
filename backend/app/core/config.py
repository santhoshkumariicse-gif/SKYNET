from typing import List, Optional
from pydantic import Field, model_validator
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "SKYNET Autonomous SOC & XDR"
    VERSION: str = "5.0.0"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"

    # Security & Auth
    SECRET_KEY: str = Field(default="skynet_super_secret_jwt_key_enterprise_2026_prod_change_me")
    HMAC_SECRET: str = Field(default="skynet_hmac_sha256_audit_key_enterprise_2026_change_me")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 120
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    AGENT_API_KEY: str = Field(default="skynet_agent_default_secret_token_2026")
    ADMIN_INITIAL_PASSWORD: Optional[str] = None

    # Database Configuration (PostgreSQL / SQLite fallback)
    DATABASE_URL: Optional[str] = None
    POSTGRES_USER: str = "skynet_admin"
    POSTGRES_PASSWORD: str = "skynet_secure_password_2026"
    POSTGRES_DB: str = "skynet_db"
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432

    # Redis Cache
    REDIS_URL: Optional[str] = None
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: Optional[str] = "skynet_redis_2026"

    # ClickHouse
    CLICKHOUSE_HOST: str = "localhost"
    CLICKHOUSE_PORT: int = 8123
    CLICKHOUSE_USER: str = "default"
    CLICKHOUSE_PASSWORD: str = "skynet_ch_password_2026"
    CLICKHOUSE_DB: str = "skynet"

    # Threat Intelligence API Keys (Optional)
    VIRUSTOTAL_API_KEY: Optional[str] = None
    ABUSEIPDB_API_KEY: Optional[str] = None
    URLHAUS_AUTH_KEY: Optional[str] = None

    # Wazuh Manager & XDR Integration
    WAZUH_ENABLED: bool = True
    WAZUH_API_URL: str = "https://localhost:55000"
    WAZUH_USER: str = "wazuh-wui"
    WAZUH_PASSWORD: str = "wazuh-wui"
    WAZUH_VERIFY_SSL: bool = False
    WAZUH_WEBHOOK_SECRET: Optional[str] = "skynet_wazuh_webhook_token_2026"

    # AI Reasoning Provider
    LLM_PROVIDER: str = "mock_heuristic" # mock_heuristic, openai, ollama
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4o"
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama3:latest"

    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8000",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8000"
    ]

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore"
    }

    @model_validator(mode="after")
    def validate_production_hardening(self) -> "Settings":
        """Enforces DevSecOps safe-fail on production startup if default secrets are detected."""
        if self.ENVIRONMENT.lower() == "production":
            insecure_jwt = "change_me" in self.SECRET_KEY or self.SECRET_KEY == "skynet_super_secret_jwt_key_enterprise_2026_prod_change_me"
            insecure_hmac = "change_me" in self.HMAC_SECRET or self.HMAC_SECRET == "skynet_hmac_sha256_audit_key_enterprise_2026_change_me"
            insecure_agent = self.AGENT_API_KEY == "skynet_agent_default_secret_token_2026"
            insecure_admin_pwd = not self.ADMIN_INITIAL_PASSWORD or self.ADMIN_INITIAL_PASSWORD == "admin123"
            
            if insecure_jwt:
                raise ValueError("CRITICAL SECURITY ERROR: Production startup aborted. Insecure default SECRET_KEY detected.")
            if insecure_hmac:
                raise ValueError("CRITICAL SECURITY ERROR: Production startup aborted. Insecure default HMAC_SECRET detected.")
            if insecure_agent:
                raise ValueError("CRITICAL SECURITY ERROR: Production startup aborted. Insecure default AGENT_API_KEY detected.")
            if insecure_admin_pwd:
                raise ValueError("CRITICAL SECURITY ERROR: Production startup aborted. Insecure default or missing ADMIN_INITIAL_PASSWORD detected.")
        return self

settings = Settings()
settings.validate_production_hardening()

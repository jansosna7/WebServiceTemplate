from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    # Podstawowe informacje
    PROJECT_NAME: str = "Modular Monolith V1.0"
    ENVIRONMENT: str = "dev"
    
    # Baza danych i Fallback[cite: 4, 5]
    USE_DB: bool = False
    DATABASE_URL: Optional[str] = None
    
    # Core Feature Flags[cite: 5]
    ENABLE_AUTH: bool = True
    ENABLE_ROLES: bool = True
    ENABLE_EVENTS: bool = True
    ENABLE_PLUGINS: bool = True
    ENABLE_BACKGROUND_TASKS: bool = True
    
    # Moduły Biznesowe (Capability Registry)[cite: 5]
    ENABLE_WALLET: bool = True
    ENABLE_LEDGER: bool = True
    ENABLE_FILES: bool = True
    ENABLE_SCRIPTS: bool = True
    
    # Web & Admin[cite: 5]
    ENABLE_ADMIN_PANEL: bool = True
    
    # API i Formatowanie[cite: 5]
    API_V1_STR: str = "/api/v1"
    ENABLE_STANDARD_RESPONSE: bool = True
    ENABLE_GLOBAL_ERROR_HANDLER: bool = True
    ENABLE_HEALTH_CHECK: bool = True
    ENABLE_METRICS: bool = True
    DEFAULT_PAGINATION_LIMIT: int = 20
    
    # Rate Limiting[cite: 5]
    ENABLE_RATE_LIMIT: bool = True
    RATE_LIMIT_WINDOW: str = "1 minute"
    RATE_LIMIT_MAX_REQUESTS: int = 100
    
    # SMTP / Email[cite: 5]
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: Optional[int] = None
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None

    # Konfiguracja Pydantic - skąd brać dane[cite: 4]
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

# Tworzymy globalną instancję ustawień do importowania w całym projekcie
settings = Settings()

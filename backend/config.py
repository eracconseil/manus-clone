from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_ignore_empty=True,  # .env values override empty system env vars
    )

    anthropic_api_key: str
    moonshot_api_key: str = ""   # Plus nécessaire — Kimi passe par OpenRouter
    openrouter_api_key: str

    supabase_url: str
    supabase_service_key: str

    e2b_api_key: str = ""
    brave_search_api_key: str = ""

    stripe_secret_key: str = ""
    stripe_webhook_secret: str = ""
    stripe_pro_price_id: str = ""
    stripe_business_price_id: str = ""

    frontend_url: str = "http://localhost:3000"
    backend_url: str = "http://localhost:8000"


settings = Settings()

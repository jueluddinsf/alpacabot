from pydantic import BaseSettings, Field

class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    danelfin_api_key: str = Field(..., env="DANELFIN_API_KEY")
    twelvedata_api_key: str = Field("", env="TWELVEDATA_API_KEY")
    alphavantage_api_key: str = Field(..., env="ALPHAVANTAGE_API_KEY")
    alpaca_api_key: str = Field(..., env="ALPACA_API_KEY")
    alpaca_api_secret: str = Field(..., env="ALPACA_SECRET")
    postgres_dsn: str = Field(..., env="POSTGRES_DSN")
    smtp_server: str = Field(..., env="SMTP_SERVER")
    smtp_port: int = Field(587, env="SMTP_PORT")
    smtp_user: str = Field(..., env="SMTP_USER")
    smtp_password: str = Field(..., env="SMTP_PASSWORD")

    class Config:
        env_file = ".env"

settings = Settings()

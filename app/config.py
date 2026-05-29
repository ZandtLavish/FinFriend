from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # Ollama
    OLLAMA_HOST: str = "http://localhost:11434"
    LLM_MODEL: str = "qwen3.6"
    
    # Chroma
    CHROMA_HOST: str = "localhost"
    CHROMA_PORT: str = "8000"
    CHROMA_TOKEN: str
    
    # External APIs
    FRED_KEY: str
    SEC_APP_NAME: str = "FinFriend"
    SEC_EMAIL: str = "yourname@email.com"
    
    log_level: str = "INFO"
    
    sec_filing_track_list: list[dict] = [
        {
        "ticker": "AAPL",
        "cik": "0000320193",
        "form_types": ["10-Q"],  # ["10-K", "10-Q", "8-K"],
        "days_back": 90
        },
    ]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="allow"
    )

settings = Settings()




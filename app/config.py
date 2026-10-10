from pydantic_settings import BaseSettings, SettingsConfigDict
class Settings(BaseSettings):
    app_name: str = "Intelligent File Deduplication System"
    secret_key: str = "replace-with-a-long-random-secret"
    access_token_expire_minutes: int = 60
    database_url: str = "sqlite:///./dedup.db"
    redis_url: str = "redis://localhost:6379/0"
    cors_origins: str = "http://localhost:5173"
    storage_dir: str = "./storage"
    max_upload_size_mb: int = 1024
    protected_file_ids: str = ""
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    @property
    def cors_list(self): return [x.strip() for x in self.cors_origins.split(",") if x.strip()]
    @property
    def protected_ids(self): return {int(x.strip()) for x in self.protected_file_ids.split(",") if x.strip().isdigit()}
settings = Settings()

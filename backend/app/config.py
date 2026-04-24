from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "AI Comparator"
    debug: bool = True

    database_url: str = "sqlite:///./app.db"

    db_echo: bool = False
    db_pool_size: int = 5
    db_max_overflow: int = 10
    db_pool_pre_ping: bool = True

    workspace_dir: str = "./workspace"
    reports_dir: str = "./reports/generated"

    class Config:
        env_file = ".env"
        extra= "ignore"

@lru_cache
def get_settings():
    return Settings()
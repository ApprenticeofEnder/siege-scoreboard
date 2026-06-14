from functools import lru_cache
from pathlib import Path

import yaml
from pydantic_settings import BaseSettings, SettingsConfigDict

from app.schemas.config import ServerConfig


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "sqlite:///./data/scoreboard.db"
    config_path: Path = Path("config/config.yaml")


@lru_cache
def get_settings() -> Settings:
    return Settings()


def load_server_config(path: Path | None = None) -> ServerConfig:
    settings = get_settings()
    config_path = path or settings.config_path
    with config_path.open() as handle:
        data = yaml.safe_load(handle)
    return ServerConfig.model_validate(data)

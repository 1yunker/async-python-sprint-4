from pydantic import PostgresDsn
from pydantic_settings import BaseSettings


class AppSettings(BaseSettings):
    app_title: str = 'Default_title'
    database_dsn: PostgresDsn | None = None
    project_host: str = '127.0.0.1'
    project_port: int = 8000

    class Config:
        env_file = '.env.example'


app_settings = AppSettings()

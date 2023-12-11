from pydantic import PostgresDsn
from pydantic_settings import BaseSettings


class AppSettings(BaseSettings):
    app_title: str = 'Default_title'
    database_dsn: PostgresDsn | None = None
    project_host: str = '127.0.0.1'
    project_port: int = 8000

    short_url_chars: str = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890'
    short_url_length: int = 6

    pagiantor_offset: int = 0
    pagiantor_limit: int = 10

    class Config:
        env_file = '.env.example'


app_settings = AppSettings()

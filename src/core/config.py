from pydantic import PostgresDsn
from pydantic_settings import BaseSettings


class AppSettings(BaseSettings):
    app_title: str = 'Get_Short_Url_App'
    database_dsn: PostgresDsn | None = None
    project_host: str
    project_port: int

    class Config:
        env_file = '.env.example'


app_settings = AppSettings()

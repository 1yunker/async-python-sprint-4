from random import choices

from api.v1 import schemas
from core import config
from models.models import URL


def generate_short_id() -> str:
    return ''.join(choices(
        config.app_settings.short_url_chars,
        k=config.app_settings.short_url_length)
    )


def create_url_obj(request_body: schemas.OriginalURL) -> URL:
    short_id = generate_short_id()
    return URL(        
        original_url=str(request_body.original_url),
        short_id=short_id,
        short_url=''.join([
            'http://',
            config.app_settings.project_host,
            ':',
            str(config.app_settings.project_port),
            '/',
            short_id])
    )


def create_list_url_obj(
        request_body: list[schemas.OriginalURL]
) -> list[URL]:
    return [
        create_url_obj(request_body[i]) for i in range(len(request_body))
    ]

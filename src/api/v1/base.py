import logging
from random import choices
from typing import Annotated

from fastapi import APIRouter, Depends, Header, Response, status

# from fastapi.exceptions import RequestValidationError
# from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing_extensions import Any, Optional, Union

from core import config
from core.logger import LOGGING
from db.db import get_session
from models.models import URL, Click

from . import schemas

router = APIRouter()

logging.basicConfig = LOGGING
logger = logging.getLogger()

# default_paginator = schemas.Paginator(limit=2, offset=0)


@router.post('/',
             response_model=schemas.GetShortURL,
             status_code=status.HTTP_201_CREATED)
async def create_url(
    request_body: schemas.CreateOriginalURL,
    db: AsyncSession = Depends(get_session),
) -> URL:
    """
    Создает сокращенный вариант переданного URL.
    """
    obj_url = URL(
        original_url=str(request_body.original_url),
        short_url=''.join(
            choices(config.app_settings.short_url_chars,
                    k=config.app_settings.short_url_length)
        )
    )
    db.add(obj_url)
    await db.commit()
    await db.refresh(obj_url)
    return obj_url


@router.post('/shorten',
             tags=['additional'],
             response_model=list[schemas.GetShortURL],
             status_code=status.HTTP_201_CREATED)
async def batch_upload_urls(
    request_body: list[schemas.CreateOriginalURL],
    db: AsyncSession = Depends(get_session),
) -> list[URL]:
    """
    Пакетно создает сокращенный вариант для переданного списка URL.
    Принимает:  [
                    {"original-url": "<URL-for-shorten>"},
                    ...
                ]
    Возвращает: [
                    {
                        "short-id": "<shoten-id>",
                        "short-url": "http://...",
                    },
                    ...
                ]
    """
    lst_obj = [
        URL(
            original_url=str(request_body[i].original_url),
            short_url=''.join(
                choices(config.app_settings.short_url_chars,
                        k=config.app_settings.short_url_length)
            )
        )
        for i in range(len(request_body))
    ]
    db.add_all(lst_obj)
    await db.flush(lst_obj)
    await db.commit()

    return lst_obj


@router.get('/ping',
            tags=['additional'])
async def ping_db(db: AsyncSession = Depends(get_session)) -> dict():
    """
    Возвращает информацию о статусе доступности БД.
    """
    try:
        await db.connection()
        status = 'Connected'
    except Exception:
        status = 'Disconnected'
    finally:
        return {'Database status': status}


@router.get('/{shorten_url_id}',
            status_code=status.HTTP_307_TEMPORARY_REDIRECT)
async def redirect_by_shorten_id(
    shorten_url_id: int,
    user_agent: Annotated[str | None, Header()] = None,
    db: AsyncSession = Depends(get_session),
) -> dict():
    """
    Возвращает ответ с кодом 307 и оригинальным URL в заголовке Location.
    """
    try:
        obj_url = await db.get(URL, shorten_url_id)
        if obj_url:
            obj_click = Click(url_id=obj_url.id, user_agent=user_agent)
            db.add(obj_click)
            obj_url.clicks += 1
            db.add(obj_url)
            await db.commit()

        return {'Location': obj_url.original_url}

    except Exception as err:
        logger.info(err)
        return Response(status_code=status.HTTP_404_NOT_FOUND)


@router.delete('/{shorten-url-id}',
               tags=['additional'])
async def set_inactive_shorten_url(
    shorten_url_id: int,
    db: AsyncSession = Depends(get_session),
) -> None:
    """
    Помечает запись с shorten-url-id как неактивную.
    """
    try:
        obj_url = await db.get(URL, shorten_url_id)
        obj_url.is_active = False
        db.add(obj_url)
        await db.commit()

    except Exception as err:
        logger.info(err)
        return Response(status_code=status.HTTP_404_NOT_FOUND)


@router.get('/{shorten-url-id}/status')
async def get_shorten_url_status(
    shorten_url_id: int,
    db: AsyncSession = Depends(get_session),
    full_info: bool = False,
    max_result: Optional[int] = config.app_settings.pagiantor_limit,
    offset: Optional[int] = config.app_settings.pagiantor_offset,
    # paginator: schemas.Paginator = Depends(default_paginator),
) -> dict():
    """
    Возвращает информацию о количестве переходов, совершенных по ссылке.
    """
    try:
        obj_url = await db.get(URL, shorten_url_id)
        if full_info:
            query = select(
                Click.created_at, Click.user_agent
            ).where(
                Click.url_id == shorten_url_id
            )
            lst_clicks = (await db.execute(query)).all()
            return {
                'Clicks': obj_url.clicks,
                # 'Clicks-info': lst_clicks[
                #     paginator.offset: paginator.offset + paginator.limit]
                'Full-info': lst_clicks[offset: offset + max_result]
            }
        else:
            return {
                'Clicks': obj_url.clicks
            }

    except Exception as err:
        logger.info(err)
        return Response(status_code=status.HTTP_404_NOT_FOUND)

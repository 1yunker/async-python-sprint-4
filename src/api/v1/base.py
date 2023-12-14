import logging
from typing import Annotated

from fastapi import APIRouter, Depends, Header, Response, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing_extensions import Optional

from core import config
from core.logger import LOGGING
from db.db import get_session
from models import URL, Click
from services import create_list_url_obj, create_url_obj

from . import schemas

router = APIRouter()

logging.basicConfig = LOGGING
logger = logging.getLogger()


@router.post('/',
             response_model=schemas.FullURL,
             status_code=status.HTTP_201_CREATED)
async def create_url(
    request_body: schemas.OriginalURL,
    db: AsyncSession = Depends(get_session),
) -> URL:
    """
    Создает сокращенный вариант переданного URL.
    """
    obj_url = create_url_obj(request_body)
    db.add(obj_url)
    await db.commit()
    await db.refresh(obj_url)
    return obj_url


@router.post('/shorten',
             tags=['additional'],
             response_model=list[schemas.ShortURL],
             status_code=status.HTTP_201_CREATED)
async def batch_upload_urls(
    request_body: list[schemas.OriginalURL],
    db: AsyncSession = Depends(get_session),
) -> list[URL]:
    """
    Пакетно создает сокращенные варианты для переданного списка URL.
    """
    lst_obj = create_list_url_obj(request_body)
    db.add_all(lst_obj)
    await db.flush(lst_obj)
    await db.commit()

    return lst_obj


@router.get('/ping',
            tags=['additional'])
async def ping_db(db: AsyncSession = Depends(get_session)) -> dict:
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
    shorten_url_id: str,
    user_agent: Annotated[str | None, Header()] = None,
    db: AsyncSession = Depends(get_session),
) -> dict:
    """
    Возвращает ответ с кодом 307 и оригинальным URL в заголовке Location.
    """
    try:
        query = select(URL).where(URL.short_id == shorten_url_id)
        obj_url = (await db.scalars(query)).first()
        if obj_url.is_active:
            obj_click = Click(url_id=obj_url.id, user_agent=user_agent)
            db.add(obj_click)
            obj_url.clicks += 1
            db.add(obj_url)
            await db.commit()

            return {'Location': obj_url.original_url}
        return Response(status_code=status.HTTP_410_GONE)

    except Exception as err:
        logger.info(err)
        return Response(status_code=status.HTTP_404_NOT_FOUND)


@router.delete('/{shorten-url-id}',
               tags=['additional'])
async def set_inactive_shorten_url(
    shorten_url_id: str,
    db: AsyncSession = Depends(get_session),
) -> None:
    """
    Помечает запись с shorten-url-id как неактивную.
    """
    try:
        query = select(URL).where(URL.short_id == shorten_url_id)
        obj_url = (await db.scalars(query)).first()
        obj_url.is_active = False
        db.add(obj_url)
        await db.commit()

    except Exception as err:
        logger.info(err)
        return Response(status_code=status.HTTP_404_NOT_FOUND)


@router.get('/{shorten-url-id}/status')
async def get_shorten_url_status(
    shorten_url_id: str,
    db: AsyncSession = Depends(get_session),
    full_info: bool = False,
    max_result: Optional[int] = config.app_settings.pagiantor_limit,
    offset: Optional[int] = config.app_settings.pagiantor_offset,
) -> dict:
    """
    Возвращает информацию о количестве переходов, совершенных по ссылке.
    """
    try:
        query = select(URL).where(URL.short_id == shorten_url_id)
        obj_url = (await db.scalars(query)).first()
        if full_info:
            query = select(
                Click.created_at, Click.user_agent
            ).where(
                Click.url_id == obj_url.id
            )
            lst_clicks = (await db.execute(query)).all()
            return {
                'Clicks': obj_url.clicks,
                'Full-info': lst_clicks[offset: offset + max_result]
            }
        else:
            return {
                'Clicks': obj_url.clicks
            }

    except Exception as err:
        logger.info(err)
        return Response(status_code=status.HTTP_404_NOT_FOUND)

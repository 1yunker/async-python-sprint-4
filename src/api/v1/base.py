from email.policy import default
import sys
from random import choices
from xmlrpc.client import Boolean

from fastapi import APIRouter, Depends, Header, Response, status
from fastapi.responses import RedirectResponse
from httpx import request
from pydantic import BaseModel, ConfigDict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import Annotated
from typing_extensions import Any, Optional, Union

from core import config
from db.db import get_session
from models.models import URL, Click

from . import schemas

router = APIRouter()
paginator = schemas.Paginator()


@router.post('/',
             response_model=schemas.GetShortURL,
             status_code=status.HTTP_201_CREATED)
async def create_url(request_body: schemas.CreateOriginalURL,
                     db: AsyncSession = Depends(get_session),):
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


@router.get('/ping', tags=['additional'])
async def ping_db(db: AsyncSession = Depends(get_session)):
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
            status_code=status.HTTP_307_TEMPORARY_REDIRECT
            )
async def redirect_by_shorten_id(
    shorten_url_id: int,
    user_agent: Annotated[str | None, Header()] = None,
    db: AsyncSession = Depends(get_session),
):
    """
    Возвращает ответ с кодом 307 и оригинальным URL в заголовке Location
    """
    obj_url = await db.get(URL, shorten_url_id)
    if obj_url:
        obj_click = Click(url_id=obj_url.id,
                          user_agent=user_agent)
        db.add(obj_click)
        obj_url.clicks += 1
        db.add(obj_url)
        await db.commit()

    return {'Location': obj_url.original_url}


@router.delete('/{shorten-url-id}', tags=['additional'])
async def set_inactive_shorten_url(shorten_url_id: int,
                                   db: AsyncSession = Depends(get_session),):
    """
    Помечает запись с shorten-url-id как неактивную.
    """
    obj_url = await db.get(URL, shorten_url_id)
    obj_url.is_active = False
    db.add(obj_url)
    await db.commit()


@router.get('/{shorten-url-id}/status')
async def get_status_shorten_url(
    shorten_url_id: int,
    db: AsyncSession = Depends(get_session),
    full_info: bool = False,
    # paginator=Depends(paginator),
):
    """
    Возвращает информацию о количестве переходов, совершенных по ссылке.
    """
    obj_url = await db.get(URL, shorten_url_id)
    if full_info:
        query = select(Click.created_at, Click.user_agent
                       ).where(Click.url_id == shorten_url_id)
        lst_clicks = (await db.execute(query)).all()
        return {
            'Clicks': obj_url.clicks,
            'Clicks-info': lst_clicks
            # 'Clicks-info': lst_clicks[
            #     paginator.offset: paginator.offset + paginator.limit]
        }
    else:
        return {
            'Clicks': obj_url.clicks
        }


# @router.post('/shorten/',
#              response_model=list[CollectionItem],
#              status_code=status.HTTP_201_CREATED)
# async def create_item(item: CollectionItem):
#     """
#     Принимает:  [
#                     {"original-url": "<URL-for-shorten>"},
#                     ...
#                 ]
#     Возвращает: [
#                     {
#                         "short-id": "<shoten-id>",
#                         "short-url": "http://...",
#                     },
#                     ...
#                 ]
#     """
#     return item

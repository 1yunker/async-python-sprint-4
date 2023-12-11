import sys

from fastapi import APIRouter, Depends, Response, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from typing_extensions import Any, Optional, Union

from db.db import get_session
from models import models
from . import schemas

router = APIRouter()


@router.get('/')
async def read_main():
    return {'msg': 'Hello World'}


@router.post('/',
             response_model=schemas.GetShortURL,
             status_code=status.HTTP_201_CREATED)
async def create_url(request_body: schemas.CreateOriginalURL,
                     db: AsyncSession = Depends(get_session),):
    """
    Создает сокращенный вариант переданного URL.
    """
    obj_url = models.URL(
        original_url=str(request_body.original_url),
        short_url=('http://127.0.0.1:8000/'
                   + str(abs(hash(request_body.original_url))))
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


@router.delete('/{shorten-url-id}', tags=['additional'])
async def delete_shorten_url(shorten_url_id):
    pass

# @router.get('/{shorten_url_id}')
# async def action_handler(shorten_url_id):
#     return {
#         'action': shorten_url_id
#     }

# @router.get('/{shorten-url-id}/status')
# async def status_handler(
#     'full-info': str,
#     param2: Optional[int] = None,
# ) -> dict[str, Union[str, int, None]]:
#     return {
#         'action': 'filter',
#         'param1': param1,
#         'param2': param2
#     }


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

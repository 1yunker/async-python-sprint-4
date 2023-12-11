import uvicorn
from fastapi import Depends, FastAPI, Header, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import ORJSONResponse
from pydantic import BaseModel, Field
from typing_extensions import Annotated, Union

from api.v1 import base
from core import config

app = FastAPI(
    title=config.app_settings.app_title,
    default_response_class=ORJSONResponse,
)
app.include_router(base.router, prefix='/api/v1')


if __name__ == '__main__':
    uvicorn.run(
        'main:app',
        host=config.app_settings.project_host,
        port=config.app_settings.project_port,
    )

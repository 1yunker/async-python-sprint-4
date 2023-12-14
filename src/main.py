import uvicorn
from fastapi import FastAPI, Request, Response, status
from fastapi.responses import ORJSONResponse

from api.v1 import base
from core import config, logger

app = FastAPI(
    title=config.app_settings.app_title,
    default_response_class=ORJSONResponse,
)
app.include_router(base.router, prefix='/api/v1')


@app.middleware('http')
async def check_allowed_ip(request: Request, call_next):
    """
    Блокирует доступ к сервису из запрещённых подсетей (black list).
    """
    if request.client.host in config.app_settings.black_list:
        return Response(status_code=status.HTTP_403_FORBIDDEN)

    return await call_next(request)


if __name__ == '__main__':
    uvicorn.run(
        'main:app',
        host=config.app_settings.project_host,
        port=config.app_settings.project_port,
        reload=True,
        log_config=logger.LOGGING
    )

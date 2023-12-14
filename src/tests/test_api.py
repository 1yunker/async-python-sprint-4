from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from core.config import app_settings
from db.db import get_session
from main import app
from models import Base

client = TestClient(app=app)


async def override_get_session() -> AsyncSession:
    engine = create_async_engine(
        str(app_settings.database_dsn),
        echo=app_settings.echo | True,
        future=True
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    async_session = sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False
    )
    async with async_session() as session:
        yield session


app.dependency_overrides[get_session] = override_get_session


def test_ping_db():
    response = client.get(
        app.url_path_for('ping_db')
    )
    assert response.status_code == 200
    assert response.json() == {'Database status': 'Connected'}


def test_create_url():
    response = client.post(
        app.url_path_for('create_url'),
        json={'original-url': 'http://example.com/'}
    )
    assert response.status_code == 201


def test_batch_upload_urls():
    data = [
        {
            'original-url': 'http://example1.com/'
        },
        {
            'original-url': 'http://example2.com/'
        }
    ]
    response = client.post(
        app.url_path_for('batch_upload_urls'),
        json=data
    )
    assert response.status_code == 201

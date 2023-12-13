from fastapi.testclient import TestClient

from main import app

client = TestClient(app=app)


def test_ping_db():
    response = client.get('api/v1/ping')
    assert response.status_code == 200
    assert response.json() == {'Database status': 'Connected'}


# def test_create_url():
#     response = client.post(
#         'api/v1/',
#         json={'original-url': 'http://example.com/'}
#     )
#     assert response.status_code == 201
#     # assert response.json() == {'Database status': 'Connected'}

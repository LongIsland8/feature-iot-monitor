# backend/tests/conftest.py


import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch  # ✅ Добавлено!

from app.main import app
from app.database import Base, engine, SessionLocal


@pytest.fixture(scope="session")
def db_engine():
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db_session(db_engine):
    connection = engine.connect()
    transaction = connection.begin()
    session = SessionLocal(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def mock_celery(mocker):
    with patch("app.api.webhooks.process_sensor_event.delay") as mock:
        yield mock
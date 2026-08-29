import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.database import SessionLocal
from app.models import User, RefreshToken


@pytest.fixture
def client():
    with TestClient(app) as client:
        yield client


@pytest.fixture(autouse=True)
def clean_database():
    db = SessionLocal()

    db.query(RefreshToken).delete()
    db.query(User).delete()

    db.commit()
    db.close()

    yield

    db = SessionLocal()

    db.query(RefreshToken).delete()
    db.query(User).delete()

    db.commit()
    db.close()
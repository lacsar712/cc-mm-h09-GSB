import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

os.environ.setdefault("DATABASE_URL", "sqlite://")

from app import main  # noqa: E402
from app.main import app  # noqa: E402


@pytest.fixture()
def client(monkeypatch):
    test_engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    monkeypatch.setattr(main, "engine", test_engine)
    monkeypatch.setattr(main, "SessionLocal", sessionmaker(bind=test_engine))
    with TestClient(app) as c:
        # startup 会播种两条示例数据，测试需要空表
        db = main.SessionLocal()
        try:
            db.query(main.Reading).delete()
            db.commit()
        finally:
            db.close()
        yield c


@pytest.fixture()
def writer_headers(client):
    res = client.post(
        "/api/auth/login", json={"username": "gasman", "password": "gas123456"}
    )
    assert res.status_code == 200
    return {"Authorization": f"Bearer {res.json()['access_token']}"}


@pytest.fixture()
def reader_headers(client):
    res = client.post(
        "/api/auth/login", json={"username": "viewer", "password": "view123456"}
    )
    assert res.status_code == 200
    return {"Authorization": f"Bearer {res.json()['access_token']}"}


@pytest.fixture()
def stored_sites():
    def _stored_sites(client, headers):
        res = client.get("/api/readings", headers=headers)
        assert res.status_code == 200
        return [r["site"] for r in res.json()]

    return _stored_sites

"""空测点放行旁路已禁用：两条写入路径都拒绝空串/纯空格，不补自动名。"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool

import app.main as main
from app.main import Reading
from sqlalchemy.orm import sessionmaker


@pytest.fixture()
def client():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    main.engine = engine
    main.SessionLocal = sessionmaker(bind=engine)
    with TestClient(main.app) as c:
        yield c


def auth(client, username, password):
    res = client.post("/api/auth/login", json={"username": username, "password": password})
    assert res.status_code == 200
    return {"Authorization": f"Bearer {res.json()['access_token']}"}


def count_rows():
    db = main.SessionLocal()
    try:
        return db.query(Reading).count()
    finally:
        db.close()


def sites_in_db():
    db = main.SessionLocal()
    try:
        return [r.site for r in db.query(Reading).all()]
    finally:
        db.close()


@pytest.mark.parametrize("path", ["/api/readings", "/api/readings/ingest"])
def test_empty_string_rejected(client, path):
    before = count_rows()
    res = client.post(path, json={"site": "", "ch4_pct": 0.4}, headers=auth(client, "gasman", "gas123456"))
    assert res.status_code == 400
    assert res.json()["detail"] == "测点名不能为空"
    assert count_rows() == before
    assert all("自动测点" not in s for s in sites_in_db())


@pytest.mark.parametrize("path", ["/api/readings", "/api/readings/ingest"])
@pytest.mark.parametrize("blank", ["   ", "\t", "\n\t ", " "])
def test_whitespace_only_rejected(client, path, blank):
    before = count_rows()
    res = client.post(path, json={"site": blank, "ch4_pct": 0.4}, headers=auth(client, "gasman", "gas123456"))
    assert res.status_code == 400
    assert res.json()["detail"] == "测点名不能为空"
    assert count_rows() == before
    assert all(not s.startswith("自动测点") for s in sites_in_db())


@pytest.mark.parametrize("path", ["/api/readings", "/api/readings/ingest"])
def test_valid_site_with_0_4_accepted(client, path):
    res = client.post(path, json={"site": "  东翼-13 ", "ch4_pct": 0.4},
                      headers=auth(client, "gasman", "gas123456"))
    assert res.status_code == 201
    body = res.json()
    assert body["site"] == "东翼-13"  # 仅去空格，不改名
    assert body["ch4_pct"] == 0.4
    assert body["level"] == "正常"
    assert "东翼-13" in sites_in_db()


@pytest.mark.parametrize("path", ["/api/readings", "/api/readings/ingest"])
def test_reader_cannot_write(client, path):
    h = auth(client, "viewer", "view123456")
    res = client.post(path, json={"site": "回风巷", "ch4_pct": 0.4}, headers=h)
    assert res.status_code == 403
    # 只读身份读列表仍然允许
    assert client.get("/api/readings", headers=h).status_code == 200


@pytest.mark.parametrize("path", ["/api/readings", "/api/readings/ingest"])
def test_anonymous_cannot_write(client, path):
    assert client.post(path, json={"site": "回风巷", "ch4_pct": 0.4}).status_code == 401

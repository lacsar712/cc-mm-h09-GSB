import pytest

WRITE_PATHS = ["/api/readings", "/api/readings/ingest"]


@pytest.mark.parametrize("path", WRITE_PATHS)
def test_empty_string_rejected(client, writer_headers, stored_sites, path):
    res = client.post(path, headers=writer_headers, json={"site": "", "ch4_pct": 0.4})
    assert res.status_code == 400
    assert res.json()["detail"] == "测点名不能为空"
    assert stored_sites(client, writer_headers) == []


@pytest.mark.parametrize("path", WRITE_PATHS)
def test_whitespace_only_rejected(client, writer_headers, stored_sites, path):
    res = client.post(path, headers=writer_headers, json={"site": "   \t ", "ch4_pct": 0.4})
    assert res.status_code == 400
    assert res.json()["detail"] == "测点名不能为空"
    assert stored_sites(client, writer_headers) == []


@pytest.mark.parametrize("path", WRITE_PATHS)
def test_valid_site_with_04_writable(client, writer_headers, stored_sites, path):
    res = client.post(
        path, headers=writer_headers, json={"site": "东翼-13", "ch4_pct": 0.4}
    )
    assert res.status_code == 201
    body = res.json()
    assert body["site"] == "东翼-13"
    assert body["ch4_pct"] == pytest.approx(0.4)
    assert body["level"] == "正常"
    assert stored_sites(client, writer_headers) == ["东翼-13"]


@pytest.mark.parametrize("path", WRITE_PATHS)
def test_surrounding_whitespace_trimmed_not_autonamed(client, writer_headers, path):
    res = client.post(
        path, headers=writer_headers, json={"site": "  回风巷  ", "ch4_pct": 0.4}
    )
    assert res.status_code == 201
    assert res.json()["site"] == "回风巷"
    assert not res.json()["site"].startswith("自动测点")


@pytest.mark.parametrize("path", WRITE_PATHS)
def test_reader_cannot_write_empty(client, reader_headers, path):
    res = client.post(path, headers=reader_headers, json={"site": "", "ch4_pct": 0.4})
    assert res.status_code == 403


@pytest.mark.parametrize("path", WRITE_PATHS)
def test_reader_cannot_write_valid(client, reader_headers, stored_sites, path):
    res = client.post(
        path, headers=reader_headers, json={"site": "东翼-13", "ch4_pct": 0.4}
    )
    assert res.status_code == 403
    assert stored_sites(client, reader_headers) == []


def test_reader_can_read(client, reader_headers):
    res = client.get("/api/readings", headers=reader_headers)
    assert res.status_code == 200


@pytest.mark.parametrize("path", WRITE_PATHS)
def test_unauthenticated_rejected(client, path):
    res = client.post(path, json={"site": "东翼-13", "ch4_pct": 0.4})
    assert res.status_code == 401

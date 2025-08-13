def test_status_ok(client):
    r = client.get("/status")
    assert r.status_code == 200
    j = r.json()
    assert j["ok"] is True
    assert "services" in j
    assert j["services"]["api"] == "up"
    assert "version" in j
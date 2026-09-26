from app import app, links


def client():
    app.config["TESTING"] = True
    links.clear()
    return app.test_client()


def test_health():
    res = client().get("/health")
    assert res.json["status"] == "ok"


def test_shorten_redirect_and_count_clicks():
    c = client()
    c.post("/shorten", data={"url": "https://example.com", "alias": "demo"})
    hit = c.get("/demo", follow_redirects=False)
    assert hit.status_code == 302
    assert hit.headers["Location"] == "https://example.com"
    data = c.get("/api/links").json
    assert data[0]["clicks"] == 1


def test_invalid_url_rejected():
    c = client()
    assert c.post("/shorten", data={"url": "not-a-url"}).status_code == 400
    assert c.post("/shorten", data={"url": "javascript:alert(1)"}).status_code == 400


def test_duplicate_alias_rejected():
    c = client()
    c.post("/shorten", data={"url": "https://a.com", "alias": "dup"})
    res = c.post("/shorten", data={"url": "https://b.com", "alias": "dup"})
    assert res.status_code == 409


def test_unknown_code_returns_404():
    c = client()
    assert c.get("/zzzzzz").status_code == 404


def test_invalid_expiry_rejected():
    c = client()
    res = c.post("/shorten", data={"url": "https://example.com", "expires_in": "-5"})
    assert res.status_code == 400


def test_valid_expiry_accepted():
    c = client()
    res = c.post("/shorten", data={"url": "https://example.com", "alias": "temp", "expires_in": "60"})
    assert res.status_code == 302
    data = c.get("/api/links").json
    assert data[0]["expires_at"] is not None
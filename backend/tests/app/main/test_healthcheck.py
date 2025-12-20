def test_healthcheck(client):
    response = client.get("/healthcheck")
    assert response.json() == {"status": "ok"}

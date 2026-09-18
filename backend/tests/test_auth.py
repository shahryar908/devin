from http import HTTPStatus


def register(client, username="alice", email="alice@test.com", password="pw12345"):
    return client.post(
        "/auth/register",
        json={"username": username, "email": email, "password": password},
    )


def test_register_returns_tokens(client):
    r = register(client)
    assert r.status_code == HTTPStatus.CREATED
    body = r.json()
    assert body["token_type"] == "bearer"
    assert body["access_token"]
    assert body["refresh_token"]


def test_register_duplicate_conflict(client):
    assert register(client).status_code == HTTPStatus.CREATED
    assert register(client).status_code == HTTPStatus.CONFLICT
    dup_email = register(client, username="bob", email="alice@test.com")
    assert dup_email.status_code == HTTPStatus.CONFLICT


def test_login_and_me(client):
    register(client)
    login = client.post(
        "/auth/login", data={"username": "alice", "password": "pw12345"}
    )
    assert login.status_code == HTTPStatus.OK
    token = login.json()["access_token"]

    me = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me.status_code == HTTPStatus.OK
    assert me.json() == {"id": 1, "username": "alice", "email": "alice@test.com"}


def test_login_wrong_password(client):
    register(client)
    r = client.post("/auth/login", data={"username": "alice", "password": "nope"})
    assert r.status_code == HTTPStatus.UNAUTHORIZED


def test_me_rejects_bad_token(client):
    r = client.get("/auth/me", headers={"Authorization": "Bearer garbage"})
    assert r.status_code == HTTPStatus.UNAUTHORIZED


def test_refresh_rotates_tokens(client):
    reg = register(client).json()
    r = client.post("/auth/refresh", json={"refresh_token": reg["refresh_token"]})
    assert r.status_code == HTTPStatus.OK
    body = r.json()
    me = client.get("/auth/me", headers={"Authorization": f"Bearer {body['access_token']}"})
    assert me.status_code == HTTPStatus.OK
    assert me.json()["username"] == "alice"


def test_refresh_rejects_access_token(client):
    reg = register(client).json()
    r = client.post("/auth/refresh", json={"refresh_token": reg["access_token"]})
    assert r.status_code == HTTPStatus.UNAUTHORIZED


def test_leaderboard_and_stats_empty(client):
    assert client.get("/leaderboard").json() == []
    assert client.get("/users/999/matches").status_code == HTTPStatus.NOT_FOUND
    assert client.get("/users/999/stats").status_code == HTTPStatus.NOT_FOUND
from app.core.security import hash_password
from app.models.user import User


async def test_login_and_me(client, app_session):
    app_session.add(User(email="admin@example.com", password_hash=hash_password("correct horse battery"), role="admin"))
    await app_session.commit()
    response = await client.post("/api/v1/auth/login", json={"email": "ADMIN@example.com", "password": "correct horse battery"})
    assert response.status_code == 200
    tokens = response.json()
    me = await client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {tokens['access_token']}"})
    assert me.status_code == 200
    assert me.json()["email"] == "admin@example.com"

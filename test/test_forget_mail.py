import pytest
from httpx import AsyncClient, ASGITransport
from unittest.mock import patch
from Library_Management.models import User
from Library_Management.utils import auth_service

@pytest.fixture()
async def test_user(override_get_db) :
    async for session in override_get_db():
        user = User(
            email="validuser1@gmail.com",
            passwords=auth_service.hash_password("SecurePass123!"),
            first_name="Test",
            last_name="User",
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)
        yield user

@pytest.mark.asyncio
async def test_forget_password_success(test_app, test_user):
    transport = ASGITransport(app=test_app)
    with patch("Library_Management.router.authApi.FastMail.send_message") as mock_send:
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            payload = {"email": test_user.email}
            response = await client.post("/forget-password", json=payload)
            assert response.status_code == 200
            assert response.json() == {"detail": "Reset link sent to your email"}
            mock_send.assert_called_once()

@pytest.mark.asyncio
async def test_forget_password_invalid_email(test_app):
    transport = ASGITransport(app=test_app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        payload = {"email": "test@gmail.com"}
        response = await client.post("/forget-password", json=payload)
        assert response.status_code == 404
        assert response.json() == {"detail": "Invlaid Email"}

@pytest.mark.asyncio
async def test_reset_password_invalid_token(test_app):
    transport = ASGITransport(app=test_app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        headers = {"Authorization": "Bearer invalidtoken"}
        payload = {"new_password": "NewSecurePass123!"}
        response = await client.post("/reset-password", headers=headers, json=payload)
        assert response.status_code == 401
        assert response.json() == {"detail": "Token is invalid or expired"}
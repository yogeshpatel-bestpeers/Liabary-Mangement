from unittest.mock import AsyncMock, patch

import pytest
from httpx import AsyncClient

from Library_Management.main import app


@pytest.mark.asyncio
@patch(
    "Library_Management.utils.auth_service.authenticate_user", new_callable=AsyncMock
)
async def test_login_invalid_credentials(mock_authenticate_user):
    # Arrange
    mock_authenticate_user.return_value = None

    async with AsyncClient(app=app, base_url="http://test") as ac:

        response = await ac.post(
            "/login",
            data={"email": "wronguser@gmail.com", "password": "wrongpassword"},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

    # Assert
    assert response.status_code == 400
    assert response.json() == {"detail": "Invalid credentials"}

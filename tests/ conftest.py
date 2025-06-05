import pytest
from httpx import AsyncClient

from Library_Management.main import app


@pytest.fixture
async def async_client():
    async with AsyncClient(app=app, base_url="http://testserver") as client:
        yield client

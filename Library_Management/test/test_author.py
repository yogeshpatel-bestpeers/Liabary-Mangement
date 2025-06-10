import pytest
from httpx import AsyncClient, ASGITransport
from starlette import status


@pytest.mark.asyncio
async def test_create_author_success(test_app, admin_test_user_token):
    transport = ASGITransport(app=test_app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        headers = {"Authorization": f"Bearer {admin_test_user_token}"}
        payload = {"name": "New Author"}
        response = await client.post("/author/create", headers=headers, json=payload)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["details"] == "Author Created Successfully"


@pytest.mark.asyncio
async def test_delete_author_success(test_app, admin_test_user_token,create_author):
    transport = ASGITransport(app=test_app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        headers = {"Authorization": f"Bearer {admin_test_user_token}"}

        id = str(create_author.id)
        print(id)
        response = await client.delete(f"/author/delete?id={id}",headers=headers)
    

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {"detail": "Author deleted successfully"}  


@pytest.mark.asyncio
async def test_update_author_success(test_app, admin_test_user_token, create_author):
    transport = ASGITransport(app=test_app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        headers = {"Authorization": f"Bearer {admin_test_user_token}"}

        payload = {
            "name": "author"
        }
        id = str(create_author.id)
        response = await client.put(f"/author/update/{id}", headers=headers, json=payload)
        print(response.text)
        assert response.status_code == status.HTTP_202_ACCEPTED
        assert response.json() == {"detail": "Author updated successfully"}



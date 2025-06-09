import pytest
from fastapi import status
from httpx import ASGITransport, AsyncClient

@pytest.mark.asyncio
async def test_create_catogory_success(test_app, admin_test_user_token):
    transport = ASGITransport(app=test_app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        headers = {"Authorization": f"Bearer {admin_test_user_token}"}
        payload ={
        "name": "Tech"
        }

        response = await client.post("/category/create", headers=headers,json=payload)
        print(response.json())


        assert response.status_code == status.HTTP_201_CREATED
        assert response.json()["details"]  == "Category Created Successfully"

@pytest.mark.asyncio
async def test_delete_catogory_success(test_app, admin_test_user_token,create_category):
    transport = ASGITransport(app=test_app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        headers = {"Authorization": f"Bearer {admin_test_user_token}"}

        id = create_category.id
        response_2 = await client.delete(f"/category/delete?id={id}", headers=headers)

        assert response_2.status_code == status.HTTP_204_NO_CONTENT

async def test_update_catogory_success(test_app, admin_test_user_token, create_category):
    transport = ASGITransport(app=test_app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        headers = {"Authorization": f"Bearer {admin_test_user_token}"}
        payload = {
            "name": "Tech"
        }

        id = create_category.id
        response_2 = await client.put(f"/category/update/{id}", headers=headers, json=payload)
        assert response_2.status_code == status.HTTP_202_ACCEPTED

@pytest.mark.asyncio
async def test_get_categories_success(test_app, admin_test_user_token, create_category):
    transport = ASGITransport(app=test_app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        headers = {"Authorization": f"Bearer {admin_test_user_token}"}
        response = await client.get("/category/get", headers=headers)
        print("RESPONSE BODY:", response.text) 
        assert response.status_code == status.HTTP_200_OK
    

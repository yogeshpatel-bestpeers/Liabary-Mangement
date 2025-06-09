import pytest
from fastapi import status
from httpx import ASGITransport, AsyncClient



@pytest.mark.asyncio
async def test_create_book_success(test_app, admin_test_user_token,create_author,create_category):
    transport = ASGITransport(app=test_app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        headers = {"Authorization": f"Bearer {admin_test_user_token}"}
        payload = {
        "name": "Tech",
        "quantity":5,
        "author_id": str(create_author.id),
        "category_id": str(create_category.id)
    }
        response = await client.post("/book/create", headers=headers,json=payload)
        print(response.text)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.json()["details"]  == "Book Created Successfully"


@pytest.mark.asyncio
async def test_delete_book_success(test_app, admin_test_user_token,create_book):
    transport = ASGITransport(app=test_app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        headers = {"Authorization": f"Bearer {admin_test_user_token}"}
        id = str(create_book.id)
        response = await client.delete(f"/book/delete?id={id}", headers=headers)
        assert response.status_code == status.HTTP_204_NO_CONTENT

@pytest.mark.asyncio
async def test_update_book_success(test_app, admin_test_user_token,create_book):
    transport = ASGITransport(app=test_app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        headers = {"Authorization": f"Bearer {admin_test_user_token}"}
        id = str(create_book.id)
        
        payload = {
            "name": "Tech",
            "quantity":5,
            "author_id": str(create_book.author_id),
            "category_id": str(create_book.category_id)
        }

        id = str(create_book.id)
        response = await client.put(f"/book/update/{id}", headers=headers,json = payload)
        assert response.status_code == status.HTTP_202_ACCEPTED

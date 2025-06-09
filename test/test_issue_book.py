import pytest
from httpx import AsyncClient, ASGITransport
from fastapi import status



@pytest.mark.asyncio
async def test_issue_book_empty_cart(test_app, test_user_token):
    transport = ASGITransport(app=test_app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        headers = {"Authorization": f"Bearer {test_user_token}"}
        response = await client.post("/book/issue", headers=headers)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json() == {"detail": "Your cart is empty."}

@pytest.mark.asyncio
async def test_issue_book_success(test_app, test_user_token, add_book_to_cart):

    transport = ASGITransport(app=test_app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        headers = {"Authorization": f"Bearer {test_user_token}"}
        response = await client.post("/book/issue", headers=headers)

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()  
        assert data["details"] == "Book(s) issued successfully"
        assert data["issued_count"] > 0
        assert "due_date" in data


@pytest.mark.asyncio
async def test_return_book_success(test_app, test_user_token, add_book_to_cart):
    transport = ASGITransport(app=test_app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        headers = {"Authorization": f"Bearer {test_user_token}"}

        response1 = await client.post("/book/issue", headers=headers)

        book_id = add_book_to_cart.book_id
        
        response2 = await client.delete(f"/book/return/{book_id}", headers=headers)
        assert response2.status_code == status.HTTP_200_OK
        json_resp2 = response2.json()
        assert "detail" in json_resp2 and "successfully" in json_resp2["detail"].lower()


@pytest.mark.asyncio
async def test_already_return_book_(test_app, test_user_token, add_book_to_cart):
    transport = ASGITransport(app=test_app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        headers = {"Authorization": f"Bearer {test_user_token}"}

        response1 = await client.post("/book/issue", headers=headers)

        book_id = add_book_to_cart.book_id
        
        response2 = await client.delete(f"/book/return/{book_id}", headers=headers)

        response3 = await client.delete(f"/book/return/{book_id}", headers=headers)

        assert response3.status_code == status.HTTP_404_NOT_FOUND
        assert response3.json()["detail"] == "Issued Book Not Found or Already Returned"


        
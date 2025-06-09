import pytest
from httpx import AsyncClient, ASGITransport
from fastapi import status

@pytest.mark.asyncio
async def test_user_signup(test_app,payload):  
    transport = ASGITransport(app=test_app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        print('transport' , test_app)

        response = await client.post("/signup", json=payload, follow_redirects=False)
        assert response.status_code == 201

@pytest.mark.asyncio
async def test_successful_login(test_app,payload):  
    transport = ASGITransport(app=test_app) 
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        
        response = await client.post("/signup", json=payload, follow_redirects=False)
        login_data = {
            "username": payload["email"],
            "password": payload["passwords"]
        }

        response = await client.post("/login", data=login_data)

        assert response.status_code == 200
        assert "access_token" in response.json()
        assert response.json()["token_type"] == "bearer"

@pytest.mark.asyncio
async def test_successful_logout(test_app, test_user_token):
    headers = {"Authorization": f"Bearer {test_user_token}"}
    
    transport = ASGITransport(app=test_app)  
    async with AsyncClient(transport=transport, base_url="http://test") as client: 
        response = await client.post("/logout", headers=headers,  follow_redirects=False)
        
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"message": "Logged out successfully"}

@pytest.mark.asyncio
async def test_successful_logout(test_app, test_user_token):
    headers = {"Authorization": f"Bearer {test_user_token}"}
    
    transport = ASGITransport(app=test_app)  
    async with AsyncClient(transport=transport, base_url="http://test") as client: 
        response = await client.post("/logout", headers=headers,  follow_redirects=False)
        
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"message": "Logged out successfully"}


@pytest.mark.asyncio
async def test_Already_logout(test_app, test_user_token):
    headers = {"Authorization": f"Bearer {test_user_token}"}
    transport = ASGITransport(app=test_app)
    
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response1 = await client.post("/logout", headers=headers)
        assert response1.status_code == 200

        response2 = await client.post("/logout", headers=headers)
        print("First logout response:", response1.json())
        print("Second logout response:", response2.json())

        assert response2.status_code == 400
        assert response2.json() == {"detail": "Token already logged out"}





































































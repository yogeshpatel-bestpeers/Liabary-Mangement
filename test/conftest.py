import pytest
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from Library_Management.main import create_app
from Library_Management.database import Base, get_db
from httpx import AsyncClient, ASGITransport

TEST_DATABASE_URL = "postgresql+asyncpg://postgres:developer@localhost/test_db"


@pytest.fixture(scope="function")
async def setup_test_db():
    print(" Setting up test DB")
    engine = create_async_engine(TEST_DATABASE_URL, echo=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    print(" Tearing down test DB")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest.fixture()
def payload():
    return {
        "email": "validuser1@gmail.com",
        "passwords": "SecurePass123!",
        "first_name": "Test",
        "last_name": "User"
    }


@pytest.fixture()
async def override_get_db(setup_test_db):
    engine = setup_test_db
    TestingSessionLocal = sessionmaker(
        bind=engine, class_=AsyncSession, expire_on_commit=False
    )

    async def _override_get_db():
        print("Using test DB session")
        async with TestingSessionLocal() as session:
            yield session

    return _override_get_db


@pytest.fixture()
def test_app(setup_test_db, override_get_db):
    app = create_app(setup_test_db)
    app.dependency_overrides[get_db] = override_get_db
    return app

@pytest.fixture
async def test_user_token(test_app, payload):
    transport = ASGITransport(app=test_app) 
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        signup_response = await client.post("/signup", json=payload)
        assert signup_response.status_code == 201


        login_data = {
            "username":payload["email"],
            "password": payload["passwords"]  
        }
        login_response = await client.post("/login", data=login_data)
        assert login_response.status_code == 200
        json_resp = login_response.json()
        assert "access_token" in json_resp
        
        return json_resp["access_token"]

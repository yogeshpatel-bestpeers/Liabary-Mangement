import pytest
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from Library_Management.main import create_app
from Library_Management.database import Base, get_db
from httpx import AsyncClient, ASGITransport
from Library_Management.models import User,Book,Cart,Author,Category
from Library_Management.utils import auth_service


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

@pytest.fixture
async def test_user_token(test_app, test_user):
    transport = ASGITransport(app=test_app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
    
        login_data = {
            "username": test_user.email,
            "password": "SecurePass123!", 
        }
        login_response = await client.post("/login", data=login_data)
        assert login_response.status_code == 200
        json_resp = login_response.json()
        assert "access_token" in json_resp

        yield json_resp["access_token"]


@pytest.fixture()
async def create_author(override_get_db):
    async for session in override_get_db():
        author = Author(name="Test Author")
        session.add(author)
        await session.commit()
        await session.refresh(author)
        yield author
        await session.delete(author)
        await session.commit()

@pytest.fixture()
async def create_category(override_get_db):
    async for session in override_get_db():
        category = Category(name="Test Category")
        session.add(category)
        await session.commit()
        await session.refresh(category)
        yield category
        await session.delete(category)
        await session.commit()

@pytest.fixture()
async def create_book(override_get_db, create_author, create_category):
    async for session in override_get_db():
        book = Book(
            name="Test Book",
            quantity=5,
            author_id=create_author.id,
            category_id=create_category.id,
        )
        session.add(book)
        await session.commit()
        await session.refresh(book)
        yield book
        await session.delete(book)
        await session.commit()

@pytest.fixture()
async def add_book_to_cart(override_get_db, create_book, test_user):
    async for session in override_get_db():
        cart_item = Cart(user_id=test_user.id, book_id=create_book.id)
        session.add(cart_item)
        await session.commit()
        await session.refresh(cart_item)
        yield cart_item
        await session.delete(cart_item)
        await session.commit()

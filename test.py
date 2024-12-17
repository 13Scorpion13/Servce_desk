import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base, get_db
from app.main import app

TEST_SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(TEST_SQLALCHEMY_DATABASE_URL, connectargs={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="module", autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def db_session():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture(scope="module")
def client():
    app.dependency_overrides[get_db] = lambda: TestingSessionLocal()
    yield TestClient(app)


def test_create_user(client):
    response = client.post(
        "/users",
        json={"telegram_id": 12345, "first_name": "Иван", "last_name": "Иванов"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["telegram_id"] == 12345
    assert data["first_name"] == "Иван"
    assert data["last_name"] == "Иванов"

def test_get_users(client, db_session):
    response = client.get("/users")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["telegram_id"] == 12345


def test_create_task(client):
    response = client.post(
        "/tasks",
        json={"user_id": 1, "manager_id": 1, "status": "открыто"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "открыто"

def test_get_tasks(client, db_session):
    response = client.get("/tasks")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["status"] == "открыто"


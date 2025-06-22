from fastapi.testclient import TestClient
from app.main import app
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base, get_db
from app.auth import get_password_hash
from app.models import User

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture
def test_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def client(test_db):
    return TestClient(app)

@pytest.fixture
def test_user(test_db):
    db = TestingSessionLocal()
    user = User(
        username="testuser",
        email="test@example.com",
        hashed_password=get_password_hash("testpassword")
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    db.close()
    return user

def test_highlight_code(client, test_user):
    # First get a token
    response = client.post(
        "/token",
        data={"username": "testuser", "password": "testpassword"}
    )
    assert response.status_code == 200
    token = response.json()["access_token"]

    # Test highlighting code
    response = client.post(
        "/highlight",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "code": "print('hello')",
            "language": "python",
            "theme": "monokai"
        }
    )
    assert response.status_code == 200
    assert "<pre>" in response.text
    assert "print(&#39;hello&#39;)" in response.text

import os

from dotenv import load_dotenv

import pytest

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from fastapi.testclient import TestClient
from fastapi  import status

from tuition.database import Base, get_db
from tuition.main import app

load_dotenv()

SQLALCHEMY_DATABASE_URL = os.getenv("SQLALCHEMY_DATABASE_URL")


engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c

@pytest.fixture(scope="module")
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.mark.parametrize(
        "full_name, email, phone_number, password, confirm_password, field_of_interest", [("new student", "canvascoder01@gmail.com", "123pass", "Password1#", "Password1#", "string")]
        )
def test_signup(client, setup_database, full_name, email, phone_number, password, confirm_password, field_of_interest):
    response = client.post(
        "/student/signup",
        json={
            "full_name": full_name,
            "email": email,
            "phone_number": phone_number,
            "field_of_interest": field_of_interest, 
            "password" : password, 
            "confirm_password": confirm_password
            }
    )
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json().get('full_name') == full_name
    assert response.json().get('email') == email
    assert response.json().get('field_of_interest') == field_of_interest
    assert response.json().get('is_verified') == False


@pytest.mark.parametrize(
        "full_name, email, phone_number, password, confirm_password, field_of_interest", [("new student", "canvascoder01@gmail.com", "123pass", "Password1#", "Password1#", "string")]
        )
def test_invalid_email_sign_up(client, setup_database, full_name, email, phone_number, password, confirm_password, field_of_interest):
    #Sign up a user with existing details
    response = client.post(
        "/student/signup",
        json={
            "full_name": full_name,
            "email": email,
            "phone_number": phone_number,
            "field_of_interest": field_of_interest,
            "password": password,
        "confirm_password" : confirm_password     }
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == "Email already exists"
    


# # @pytest.mark.parametrize("username, phone_number", [("newuser2@example.com", "123")])
# # def test_login(client, setup_database, username, email, phone_number):
    
 
from tuition.student.models import Student
from unittest.mock import AsyncMock, patch
from sqlalchemy.future import select
import pytest

sign_up_data_1 = {
        "full_name": "Test User",
        "email": "movetey90@abevw.com",  #Use a unique email address
        "phone_number": "1234567890",
        "password": "Test#1234",
        "confirm_password": "Test#1234",
        "field_of_interest": "Computer Science"
    }
login_data = {
    "username": sign_up_data_1["email"],  
    "password": sign_up_data_1["password"]
}

@pytest.mark.asyncio
async def test_sign_up_student(test_client, fake_db_dependency):
    # Mock the student data
    mock_student = AsyncMock()
    mock_student.full_name = sign_up_data_1["full_name"]
    # Mock the SMTP service and background task
    smtp_service = AsyncMock()
    background_task = AsyncMock()
    # Mock the database execute result
    result_mock = AsyncMock()
    result_mock.scalar_one_or_none.return_value = mock_student  # Return mock_student when queried
    # Mock the db execute to return the mocked result
    fake_db_dependency.execute.return_value = result_mock

    with patch('tuition.emails_utils.SmtpMailService', return_value=smtp_service):
        with patch('fastapi.BackgroundTasks', return_value=background_task):  # Mock the BackgroundTasks
            # Make the request
            response = test_client.post("/student/signup", json=sign_up_data_1)

            # Validate the response
            assert response.status_code == 201

            # Verify student in database using select
            stmt = select(Student).where(Student.email == sign_up_data_1["email"])
            result = await fake_db_dependency.execute(stmt)

            student_in_db = await result.scalar_one_or_none()

            assert student_in_db is not None
            assert student_in_db.full_name == sign_up_data_1["full_name"]

@pytest.mark.asyncio
def test_invalid_sign_up_data(test_client, fake_db_dependency):
#Bad Request as email already in use
    response = test_client.post("/student/signup", json=sign_up_data_1)
    assert response.status_code == 400
    assert response.json()["detail"] == "Email already exists"

@pytest.mark.asyncio
def test_login(test_client, fake_db_dependency):
    #     # Create mock student object
    # mock_student = AsyncMock()
    # mock_student.email = login_data["username"]
    # mock_student.password = login_data["password"]
    # mock_student.verified = True  # Set the user as verified
    # # Mock the database call
    # result_mock = AsyncMock()
    # result_mock.scalar_one_or_none.return_value = mock_student
    # fake_db_dependency.execute.return_value = result_mock
    response = test_client.post(
        "/auth/login",
        data=login_data,  # use 'data' for form-encoded payload
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    assert response.status_code == 200
    assert response.json()["token_type"] == "bearer"

@pytest.mark.asyncio
def test_login_account_unverified(test_client, fake_db_dependency):

    response = test_client.post(
        "/auth/login",
        data=login_data,  # use 'data' for form-encoded payload
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Account not verified, check email for verification link"

# @pytest.mark.asyncio
# def test_password_incorrect(test_client, fake_db_dependency):
#     response = test_client.post(
#         "/auth/login",
#         data={
#             "username": sign_up_data_1["email"],  
#             "password": "wrong password"
#         },  # use 'data' for form-encoded payload
#         headers={"Content-Type": "application/x-www-form-urlencoded"}
#     )
#     assert response.status_code == 401
#     assert response.json()["detail"] == "Invalid credentials"


# from tuition.student_utils import get_student_by_email
from tuition.emails_utils import SmtpMailService
from fastapi import BackgroundTasks
from tuition.student.crud import reset_password  # Ensure correct import

@pytest.mark.asyncio
async def test_reset_password_called_once(fake_db_dependency, test_client):
    # Mock student data
    mock_student = AsyncMock()
    mock_student.email = "student@example.com"

    # Mock the DB response
    fake_db_dependency.scalar_one_or_none.return_value = mock_student

    # Mock background task and SMTP service
    smtp_service_mock = AsyncMock()
    background_task_mock = AsyncMock()

    with patch("tuition.student_utils.get_student_by_email", return_value=mock_student):
        with patch("tuition.emails_utils.SmtpMailService.send_password_reset_email", smtp_service_mock):
            # Call the reset_password function
            response = await reset_password(fake_db_dependency, mock_student.email, background_task_mock)

            # Ensure the email service was called once
            smtp_service_mock.assert_called_once_with(user="student")
            assert response.status_code == 200
            assert response.json()["message"] == "Reset link sent to Email"

    




# @pytest.mark.asyncio
# async def test_invalid_sign_up_data(fake_db_dependency, test_client):
#     async with AsyncClient(app=test_client, base_url="http://test") as client:
#         response = await client.post("/student/signup", json=sign_up_data_1)
#         assert response.status_code == 400

# @pytest.mark.asyncio
# async def test_invalid_sign_up_data(fake_db_dependency, test_client):
#     async with AsyncClient(app=app, base_url="http://test") as client:
#         response = await client.post("/student/signup", json=sign_up_data_1)
#         assert response.status_code == 400


    
 
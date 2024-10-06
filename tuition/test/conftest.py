import pytest
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from tuition.database import Base, db_dependency, get_db  # Adjust as needed
from tuition.main import app  # Ensure the FastAPI app is imported

# mock_db = AsyncMock()
# async def get_mock_db_dependency():
#     yield mock_db
# # Setup the test database engine
# DATABASE_URL = "sqlite+aiosqlite:///./tuition_test.db"

# engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=True)

# # engine = create_async_engine(DATABASE_URL, connect_args={"check_same_thread": False})
# TestingSessionLocal = sessionmaker(class_=AsyncSession, autocommit=False, autoflush=False, bind=engine)
# async def overide_get_db():
#     async with TestingSessionLocal as db:
#         try:
#             yield db
#         finally:
#             await db.close()
# app.dependency_overrides[get_db] = overide_get_db

# @pytest.fixture(scope="module")
# def test_client():
#     with TestClient(app) as client:
#         yield client

# @pytest.fixture(scope="module")
# async def setup_database():
#     async with engine.begin() as conn:
#         await conn.run_sync(Base.metadata.create_all)
#     yield
#     async with engine.begin() as conn:
#         await conn.run_sync(Base.metadata.drop_all)
# @pytest.fixture
# def fake_db_dependency():
#     return mock_db 


# ---!!! Your Define the mock database dependency
mock_db = AsyncMock()

async def get_mock_db_dependency():
    yield mock_db
# Override the dependency in your FastAPI app
app.dependency_overrides[db_dependency] = get_mock_db_dependency
@pytest.fixture
def fake_db_dependency():
    return mock_db  # Provide the mock dependency for tests

@pytest.fixture(scope="module")
def test_client():
    with TestClient(app) as client:
        yield client
# ---!!! Your test functions should be able to access the mocked database now

# mock_student_crud = AsyncMock()
# @pytest.fixture
# def fake_student_utils():
#      return mock_student_crud






# from fastapi.testclient import TestClient
# import pytest

# from tuition.emails_utils import SmtpMailService
# from tuition.security.oauth2 import get_current_user

# # Test running faster and do not connect to db
# from tuition.main import app
# # from tuition.database import db_dependency
# # Helps to create mock db of all mock object
# from unittest.mock import Mock

# mock_dependency = Mock()

# mock_institution_utils = AsyncMock()
# mock_student_utils = AsyncMock()
# @pytest.fixture
# def fake_student_utils():
#      return mock_student_utils
# mock_student_crud = Mock()

# # mock_student_sign_up = Mock()
# # mock_Smtp_service = Mock()
# mock_background_task = Mock()


# # mock_smtp_service = Mock(spec=SmtpMailService)

# # mock_smtp_service.send_verification_email = Mock()

# # async def get_mock_db_dependency():
# #     yield mock_dependency

# # current_user = get_current_user()

# # app.dependency_overrides[db_dependency] = get_mock_db_dependency
# # app.dependency_overrides[current_user] = Mock()

# @pytest.fixture
# def fake_db_dependency():
#     return mock_dependency

# @pytest.fixture
# def fake_student_utils():
#      return mock_student_utils

# @pytest.fixture
# def fake_institution_utils():
#      return mock_institution_utils
     
# @pytest.fixture
# def fake_student_crud():
#     return mock_student_crud

# @pytest.fixture
# def test_client():
#    return TestClient(app)

# @pytest.fixture
# def fake_background_task():
#     return mock_background_task
# # mock_smtp_service = Mock(spec=SmtpMailService)
# # mock_smtp_service.send_verification_email = Mock()
# # return mock_Smtp_service




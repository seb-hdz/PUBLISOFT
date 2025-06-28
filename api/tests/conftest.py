import os
os.environ["DATABASE_USER"] = "test_user"
os.environ["DATABASE_PWD"] = "test_password"
os.environ["DATABASE_HOST"] = "localhost"
os.environ["DATABASE_PORT"] = "5432"
os.environ["DATABASE_NAME"] = "test_db"
os.environ["JWT_SECRET"] = "test_jwt_secret_key_for_testing_purposes_only"

# Now import the rest
import pytest
import asyncio
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import StaticPool
from unittest.mock import Mock, patch
import os
import tempfile
import shutil

# Import database models and components
from modules.auth.infrastructure.unit_of_work import SqlAlchemyUnitOfWork
from modules.auth.application.message_bus import MessageBus
from modules.auth.infrastructure.database.repositories.user_repository import UserRepositorySQLAlchemy

# Create a test base for database models
TestBase = declarative_base()


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def test_database():
    """Create a test database for the test session."""
    # Create an in-memory SQLite database for testing
    test_engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    
    # Create all tables
    TestBase.metadata.create_all(bind=test_engine)
    
    # Create a session factory
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
    
    yield test_engine, TestingSessionLocal
    
    # Clean up
    TestBase.metadata.drop_all(bind=test_engine)


@pytest.fixture
def db_session(test_database):
    """Create a database session for each test."""
    engine, SessionLocal = test_database
    session = SessionLocal()
    try:
        yield session
    finally:
        session.rollback()
        session.close()


@pytest.fixture
def client(test_database):
    """Create a test client for the FastAPI application."""
    # Import the app here to avoid issues during test discovery
    from main import app
    
    # Override the database engine for testing
    test_engine, _ = test_database
    
    # Patch the engine in the main app
    with patch('common.session.engine', test_engine):
        with TestClient(app) as test_client:
            yield test_client


@pytest.fixture
def mock_unit_of_work(db_session):
    """Create a mock unit of work for testing."""
    uow = Mock(spec=SqlAlchemyUnitOfWork)
    uow.session = db_session
    uow.__enter__ = Mock(return_value=uow)
    uow.__exit__ = Mock(return_value=None)
    return uow


@pytest.fixture
def mock_message_bus():
    """Create a mock message bus for testing."""
    return Mock(spec=MessageBus)


@pytest.fixture
def mock_user_repository():
    """Create a mock user repository for testing."""
    return Mock(spec=UserRepositorySQLAlchemy)


@pytest.fixture
def sample_user_data():
    """Sample user data for testing."""
    return {
        "email": "test@example.com",
        "password": "testpassword123",
        "name": "Test",
        "last_name": "User"
    }


@pytest.fixture
def sample_login_data():
    """Sample login data for testing."""
    return {
        "email": "test@example.com",
        "password": "testpassword123"
    }


@pytest.fixture
def auth_headers():
    """Sample authentication headers for testing."""
    return {
        "Authorization": "Bearer test_token"
    }


# Environment variables for testing
@pytest.fixture(autouse=True)
def setup_test_env():
    """Set up test environment variables."""
    os.environ["DATABASE_USER"] = "test_user"
    os.environ["DATABASE_PWD"] = "test_password"
    os.environ["DATABASE_HOST"] = "localhost"
    os.environ["DATABASE_PORT"] = "5432"
    os.environ["DATABASE_NAME"] = "test_db"
    os.environ["JWT_SECRET"] = "test_jwt_secret_key_for_testing_purposes_only"
    yield 
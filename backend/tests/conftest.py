"""
Pytest configuration and fixtures for OpenPolicy Merge tests
"""

import pytest
import asyncio
from typing import Generator, AsyncGenerator
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from api.main import app
from config.database import get_database_session

# Test database URL - Using main database for testing
TEST_DATABASE_URL = "postgresql://openpolicy:openpolicy123@localhost:5432/openpolicy"

# Create test engine
test_engine = create_engine(
    TEST_DATABASE_URL,
    poolclass=StaticPool
)

# Create test session factory
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
def db_session():
    """Create a fresh database session for each test."""
    connection = test_engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture
def client(db_session) -> Generator:
    """Create a test client with database session."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_database_session] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()

@pytest.fixture
def auth_headers():
    """Get authentication headers for admin user."""
    return {
        "Authorization": "Bearer test_admin_token"
    }

@pytest.fixture
def sample_policy_data():
    """Sample policy data for testing."""
    return {
        "title": "Test Policy",
        "description": "A test policy for testing purposes",
        "jurisdiction": "federal",
        "status": "active",
        "introduced_date": "2024-01-01",
        "sponsor": "Test Sponsor"
    }

@pytest.fixture
def sample_representative_data():
    """Sample representative data for testing."""
    return {
        "name": "Test Representative",
        "party": "Test Party",
        "jurisdiction": "federal",
        "constituency": "Test Constituency",
        "email": "test@example.com",
        "phone": "123-456-7890"
    }

@pytest.fixture
def sample_scraper_data():
    """Sample scraper data for testing."""
    return {
        "name": "test_scraper",
        "jurisdiction": "federal",
        "status": "active",
        "last_run": "2024-01-01T00:00:00Z",
        "records_scraped": 100
    }

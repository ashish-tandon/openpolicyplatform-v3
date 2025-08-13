"""
Pytest configuration and fixtures for OpenPolicy Merge tests
"""

import pytest
import asyncio
import os
from typing import Generator, AsyncGenerator
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from api.main import app
from config.database import get_database_session
import jwt

TEST_JWT_SECRET = "test_secret_key"

# Determine test database URL with environment overrides and safe fallbacks
TEST_DATABASE_URL = (
    os.getenv("TEST_DATABASE_URL")
    or os.getenv("DATABASE_URL")
    or "sqlite+pysqlite:///:memory:"
)

# Create test engine (use in-memory SQLite with StaticPool when applicable)
if TEST_DATABASE_URL.startswith("sqlite"):
    test_engine = create_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
else:
    test_engine = create_engine(
        TEST_DATABASE_URL,
        poolclass=StaticPool,
    )

# Create test session factory
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


def _ensure_minimal_test_schema(connection):
    """Create minimal tables used by tests when using SQLite."""
    # users_user table used by tests/api/test_authentication_api.py
    connection.exec_driver_sql(
        """
        CREATE TABLE IF NOT EXISTS users_user (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            email TEXT,
            password_hash TEXT,
            first_name TEXT,
            last_name TEXT,
            is_active BOOLEAN,
            is_admin BOOLEAN
        )
        """
    )
    # auth_user table used by tests/api/test_enhanced_authentication.py
    connection.exec_driver_sql(
        """
        CREATE TABLE IF NOT EXISTS auth_user (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            email TEXT,
            password TEXT,
            is_active BOOLEAN,
            is_staff BOOLEAN
        )
        """
    )


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
    # Ensure schema exists for tests
    _ensure_minimal_test_schema(connection)
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
    token = jwt.encode({"sub": "admin", "type": "access"}, TEST_JWT_SECRET, algorithm="HS256")
    return {"Authorization": f"Bearer {token}"}


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

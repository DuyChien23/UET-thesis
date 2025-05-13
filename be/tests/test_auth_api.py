import pytest
from httpx import AsyncClient
import json
import logging
import asyncio
from unittest import mock

from tests.test_config import setup_test_db, cleanup_test_db

# Set up logging
logger = logging.getLogger(__name__)


@pytest.fixture(scope="module", autouse=True)
async def setup_and_teardown():
    """Set up before and tear down after all tests in this module."""
    # Setup
    await setup_test_db()
    
    yield
    
    # Teardown
    await cleanup_test_db()


@pytest.mark.asyncio
async def test_register_user(async_client: AsyncClient):
    """Test user registration."""
    logger.info("Starting test_register_user")
    try:
        # Create user data
        user_data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "securepassword123",
            "full_name": "New Test User"
        }
        
        logger.info("Making registration request")
        # Make the request
        response = await async_client.post(
            "/api/v1/auth/register",
            json=user_data
        )
        
        logger.info(f"Response received: status={response.status_code}")
        # Check response
        assert response.status_code == 201
        data = response.json()
        logger.info(f"Response data: {data}")
        assert data["username"] == user_data["username"]
        assert data["email"] == user_data["email"]
        assert data["full_name"] == user_data["full_name"]
        assert "id" in data
        assert "roles" in data
        logger.info("test_register_user completed successfully")
    except Exception as e:
        logger.error(f"Error in test_register_user: {str(e)}")
        raise


@pytest.mark.asyncio
async def test_register_duplicate_username(async_client: AsyncClient, test_user):
    """Test registering a user with existing username."""
    # Create user data with existing username
    user_data = {
        "username": "testuser",  # Already exists
        "email": "different@example.com",
        "password": "securepassword123",
        "full_name": "Duplicate User"
    }
    
    # Make the request
    response = await async_client.post(
        "/api/v1/auth/register",
        json=user_data
    )
    
    # Check response
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "Username already registered" in data["detail"]


@pytest.mark.asyncio
async def test_register_duplicate_email(async_client: AsyncClient, test_user):
    """Test registering a user with existing email."""
    # Create user data with existing email
    user_data = {
        "username": "differentuser",
        "email": "testuser@example.com",  # Already exists
        "password": "securepassword123",
        "full_name": "Duplicate Email User"
    }
    
    # Make the request
    response = await async_client.post(
        "/api/v1/auth/register",
        json=user_data
    )
    
    # Check response
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "Email already registered" in data["detail"]


@pytest.mark.asyncio
async def test_login_with_username(async_client: AsyncClient, test_user):
    """Test user login with username using OAuth2 form data."""
    # Login data as form
    login_data = {
        "username": "testuser",
        "password": "testpassword123"
    }
    
    # Make the request with form data
    response = await async_client.post(
        "/api/v1/auth/token",
        data=login_data,
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    
    # Check response
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert "expires_in" in data


@pytest.mark.asyncio
async def test_login_with_email(async_client: AsyncClient, test_user):
    """Test user login with email using OAuth2 form data."""
    # Login data as form
    login_data = {
        "username": "testuser@example.com",
        "password": "testpassword123"
    }
    
    # Make the request with form data
    response = await async_client.post(
        "/api/v1/auth/token",
        data=login_data,
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    
    # Check response
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert "expires_in" in data


@pytest.mark.asyncio
async def test_login_invalid_credentials(async_client: AsyncClient, test_user):
    """Test login with invalid credentials using OAuth2 form data."""
    # Login data with wrong password
    login_data = {
        "username": "testuser",
        "password": "wrongpassword"
    }
    
    # Make the request with form data
    response = await async_client.post(
        "/api/v1/auth/token",
        data=login_data,
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    
    # Check response
    assert response.status_code == 401
    data = response.json()
    assert "detail" in data
    assert "Incorrect username or password" in data["detail"]


@pytest.mark.asyncio
async def test_regular_login_with_json(async_client: AsyncClient, test_user):
    """Test user login using JSON payload with regular endpoint."""
    # Login data as JSON
    login_data = {
        "username": "testuser",
        "password": "testpassword123"
    }
    
    # Make the request with JSON data
    response = await async_client.post(
        "/api/v1/auth/login",
        json=login_data
    )
    
    # Check response
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert "expires_in" in data


@pytest.mark.asyncio
async def test_get_profile(async_client: AsyncClient, test_user, auth_token):
    """Test getting user profile."""
    # Make the request with authentication
    response = await async_client.get(
        "/api/v1/auth/profile",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    
    # Check response
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == test_user["username"]
    assert data["email"] == test_user["email"]
    assert data["full_name"] == test_user["full_name"]
    assert "roles" in data
    # No need to check specific roles as the format may vary


@pytest.mark.asyncio
async def test_get_profile_no_auth(async_client: AsyncClient):
    """Test getting user profile without authentication."""
    # Make the request without authentication
    response = await async_client.get("/api/v1/auth/profile")
    
    # Check response
    assert response.status_code == 403  # Forbidden or 401 Unauthorized
    

@pytest.mark.asyncio
async def test_update_profile(async_client: AsyncClient, test_user, auth_token):
    """Test updating user profile."""
    # Update data
    update_data = {
        "full_name": "Updated Test User",
        "email": "updated@example.com"
    }
    
    # Make the request with authentication
    response = await async_client.put(
        "/api/v1/auth/profile",
        json=update_data,
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    
    # Check response
    assert response.status_code == 200
    data = response.json()
    assert data["full_name"] == update_data["full_name"]
    assert data["email"] == update_data["email"]


@pytest.mark.asyncio
async def test_change_password(async_client: AsyncClient, test_user, auth_token):
    """Test changing user password."""
    # Password change data
    password_data = {
        "current_password": "testpassword123",
        "new_password": "newsecurepassword123"
    }
    
    # Make the request with authentication
    response = await async_client.post(
        "/api/v1/auth/change-password",
        json=password_data,
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    
    # Check response
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "Password changed successfully" in data["message"]
    
    # Try login with new password using OAuth2 form data
    login_data = {
        "username": "testuser",
        "password": "newsecurepassword123"
    }
    
    login_response = await async_client.post(
        "/api/v1/auth/token",
        data=login_data,
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    
    assert login_response.status_code == 200 


@pytest.mark.asyncio
async def test_basic_user_creation(async_client: AsyncClient):
    """Test the basic user creation without role assignments."""
    logger.info("Starting test_basic_user_creation")
    try:
        # Create user data
        user_data = {
            "username": "simpleuser",
            "email": "simple@example.com",
            "password": "simplepassword123",
            "full_name": "Simple User"
        }
        
        logger.info("Making registration request")
        # Make the request
        response = await async_client.post(
            "/api/v1/auth/register",
            json=user_data
        )
        
        logger.info(f"Response received: status={response.status_code}")
        # Check response
        assert response.status_code == 201
        data = response.json()
        logger.info(f"Response data: {data}")
        assert data["username"] == user_data["username"]
        assert data["email"] == user_data["email"]
        assert data["full_name"] == user_data["full_name"]
        assert "id" in data
        logger.info("test_basic_user_creation completed successfully")
    except Exception as e:
        logger.error(f"Error in test_basic_user_creation: {str(e)}")
        raise 
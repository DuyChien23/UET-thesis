import pytest
from httpx import AsyncClient
import json


@pytest.mark.asyncio
async def test_register_user(async_client: AsyncClient, init_test_db):
    """Test registering a new user."""
    # Create user data
    user_data = {
        "username": "newuser",
        "email": "newuser@example.com",
        "password": "securepassword123",
        "full_name": "New User"
    }
    
    # Make the request
    response = await async_client.post(
        "/api/v1/auth/register",
        json=user_data
    )
    
    # Check response
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == user_data["username"]
    assert data["email"] == user_data["email"]
    assert data["full_name"] == user_data["full_name"]
    assert "id" in data
    assert "roles" in data
    assert "user" in data["roles"]


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
    """Test user login with username."""
    # Login data
    login_data = {
        "username": "testuser",
        "password": "testpassword123"
    }
    
    # Make the request
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
async def test_login_with_email(async_client: AsyncClient, test_user):
    """Test user login with email."""
    # Login data
    login_data = {
        "username": "testuser@example.com",
        "password": "testpassword123"
    }
    
    # Make the request
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
async def test_login_invalid_credentials(async_client: AsyncClient, test_user):
    """Test login with invalid credentials."""
    # Login data with wrong password
    login_data = {
        "username": "testuser",
        "password": "wrongpassword"
    }
    
    # Make the request
    response = await async_client.post(
        "/api/v1/auth/login",
        json=login_data
    )
    
    # Check response
    assert response.status_code == 401
    data = response.json()
    assert "detail" in data
    assert "Incorrect username or password" in data["detail"]


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
    assert data["username"] == test_user.username
    assert data["email"] == test_user.email
    assert data["full_name"] == test_user.full_name
    assert "roles" in data


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
    
    # Try login with new password
    login_data = {
        "username": "testuser",
        "password": "newsecurepassword123"
    }
    
    login_response = await async_client.post(
        "/api/v1/auth/login",
        json=login_data
    )
    
    assert login_response.status_code == 200 
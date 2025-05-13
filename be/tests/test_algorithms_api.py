import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_get_algorithms(async_client: AsyncClient, test_user, auth_token):
    """Test getting all supported algorithms."""
    # Make the request with authentication
    response = await async_client.get(
        "/api/v1/algorithms/",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    
    # Check response
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "count" in data
    assert isinstance(data["items"], list)
    assert data["count"] == len(data["items"])
    
    # Check algorithm structure
    if data["count"] > 0:
        algorithm = data["items"][0]
        assert "name" in algorithm
        assert "type" in algorithm
        assert "is_default" in algorithm
        assert "curves" in algorithm
        assert "supported_key_formats" in algorithm


@pytest.mark.asyncio
async def test_get_default_algorithm(async_client: AsyncClient, test_user, auth_token):
    """Test getting the default algorithm."""
    # Make the request with authentication
    response = await async_client.get(
        "/api/v1/algorithms/default",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    
    # Check response
    assert response.status_code == 200
    data = response.json()
    assert "name" in data
    assert "type" in data
    assert data["is_default"] is True
    assert "curves" in data
    assert "supported_key_formats" in data


@pytest.mark.asyncio
async def test_get_specific_algorithm(async_client: AsyncClient, test_user, auth_token):
    """Test getting a specific algorithm."""
    # First get all algorithms to find a valid one
    all_response = await async_client.get(
        "/api/v1/algorithms/",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    
    all_data = all_response.json()
    if all_data["count"] == 0:
        pytest.skip("No algorithms available for testing")
    
    algorithm_name = all_data["items"][0]["name"]
    
    # Make the request for specific algorithm
    response = await async_client.get(
        f"/api/v1/algorithms/{algorithm_name}",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    
    # Check response
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == algorithm_name


@pytest.mark.asyncio
async def test_get_nonexistent_algorithm(async_client: AsyncClient, test_user, auth_token):
    """Test getting a non-existent algorithm."""
    # Make the request for non-existent algorithm
    response = await async_client.get(
        "/api/v1/algorithms/nonexistent-algorithm",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    
    # Check response
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data


@pytest.mark.asyncio
async def test_get_algorithms_no_auth(async_client: AsyncClient):
    """Test getting algorithms without authentication."""
    # Make the request without authentication
    response = await async_client.get("/api/v1/algorithms/")
    
    # Check response
    assert response.status_code == 403  # Forbidden 
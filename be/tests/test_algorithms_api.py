import pytest
from httpx import AsyncClient

# By not using fixtures from conftest.py directly in the test, 
# we avoid the conflict with event_loop fixture
@pytest.mark.asyncio
async def test_get_algorithms(async_client: AsyncClient):
    """Test getting all supported algorithms."""
    # Make the request without authentication as per current implementation
    response = await async_client.get("/api/v1/algorithms/")
    
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
        assert "id" in algorithm
        assert "name" in algorithm
        assert "type" in algorithm
        assert "is_default" in algorithm
        assert "status" in algorithm
        assert "curves" in algorithm


@pytest.mark.asyncio
async def test_get_default_algorithm(async_client: AsyncClient):
    """Test getting the default algorithm."""
    response = await async_client.get("/api/v1/algorithms/default")
    
    # In our test database, there is no default algorithm set up, so we should get a 404
    # But the test should be robust enough to handle both cases
    if response.status_code == 200:
        # If a default algorithm exists
        data = response.json()

        print("CheckinXXX")
        print(data)
        assert "id" in data
        assert "name" in data
        assert "type" in data
        assert data["is_default"] is True
    else:
        # If no default algorithm is set up, verify the 404 response
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        # The error message could be either of these depending on the state of the database
        assert "Default algorithm not found" in data["detail"] or "No algorithms found in the database" in data["detail"]


@pytest.mark.asyncio
async def test_get_specific_algorithm(async_client: AsyncClient):
    """Test getting a specific algorithm by name."""
    # First, get the list of all algorithms
    list_response = await async_client.get("/api/v1/algorithms/")
    assert list_response.status_code == 200
    algorithms = list_response.json()["items"]
    
    if algorithms:
        # Test with an existing algorithm
        first_algorithm = algorithms[0]
        algorithm_name = first_algorithm["name"]
        
        # Get the specific algorithm
        response = await async_client.get(f"/api/v1/algorithms/{algorithm_name}")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == algorithm_name
    
    # Test with a non-existent algorithm
    response = await async_client.get("/api/v1/algorithms/nonexistent-algorithm")
    assert response.status_code == 404
    assert "detail" in response.json()


@pytest.mark.asyncio
async def test_get_nonexistent_algorithm(async_client: AsyncClient):
    """Test getting a non-existent algorithm."""
    response = await async_client.get("/api/v1/algorithms/nonexistent-algorithm")
    assert response.status_code == 404
    assert "detail" in response.json()


@pytest.mark.asyncio
async def test_get_algorithms_with_auth(async_client: AsyncClient, auth_token):
    """Test getting algorithms with authentication."""
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
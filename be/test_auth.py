import asyncio
import httpx
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_register():
    """Test user registration directly with httpx."""
    logger.info("Starting test_register")
    
    # Create user data
    user_data = {
        "username": "newuser",
        "email": "newuser@example.com",
        "password": "securepassword123",
        "full_name": "New Test User"
    }
    
    logger.info("Making registration request")
    # Make the request
    async with httpx.AsyncClient(base_url="http://localhost:8000") as client:
        response = await client.post("/api/v1/auth/register", json=user_data)
    
    logger.info(f"Response received: status={response.status_code}")
    logger.info(f"Response data: {response.text}")
    
    if response.status_code == 201:
        data = response.json()
        logger.info(f"Registration successful: {data}")
    else:
        logger.error(f"Registration failed: {response.text}")

if __name__ == "__main__":
    asyncio.run(test_register()) 
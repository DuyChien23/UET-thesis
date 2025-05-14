import pytest
from httpx import AsyncClient
import uuid
import base64
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes, serialization

# Mock data
test_document = "This is a test document content."
test_metadata = {"filename": "test.txt", "filesize": 128}


async def generate_test_key_pair():
    """Generate a test RSA key pair for testing."""
    # Generate a private key
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )
    
    # Get the public key
    public_key = private_key.public_key()
    
    # Serialize the keys
    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    ).decode('utf-8')
    
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    ).decode('utf-8')
    
    return {
        'private_key': private_key,
        'public_key': public_key,
        'private_pem': private_pem,
        'public_pem': public_pem
    }


async def create_test_public_key(async_client, auth_token, key_data):
    """Create a test public key in the system."""
    # Create public key
    key_payload = {
        "key": key_data['public_pem'],
        "algorithm": "RSA-SHA256",
        "name": "Test Key",
        "description": "Test key for verification"
    }
    
    response = await async_client.post(
        "/api/public-keys/",
        json=key_payload,
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    
    return response.json()


@pytest.mark.asyncio
async def test_verify_signature(async_client: AsyncClient, test_user, auth_token):
    """Test verifying a digital signature."""
    # Skip test if test_user is None or doesn't have expected structure
    if not test_user or not isinstance(test_user, dict) or "id" not in test_user:
        pytest.skip("Test user not available or invalid")
        
    # Generate test key pair
    key_data = await generate_test_key_pair()
    
    # Create a test public key
    public_key = await create_test_public_key(async_client, auth_token, key_data)
    
    # Hash the document
    document_hash_raw = hashes.Hash(hashes.SHA256())
    document_hash_raw.update(test_document.encode())
    document_hash = document_hash_raw.finalize()
    document_hash_b64 = base64.b64encode(document_hash).decode('utf-8')
    
    # Sign the document hash with the private key
    signature_raw = key_data['private_key'].sign(
        document_hash,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )
    signature_b64 = base64.b64encode(signature_raw).decode('utf-8')
    
    # Create verification request
    verification_request = {
        "document_hash": document_hash_b64,
        "signature": signature_b64,
        "public_key_id": public_key["id"],
        "algorithm_name": "RSA-SHA256",
        "document_id": str(uuid.uuid4()),
        "metadata": test_metadata
    }
    
    # Make verification request
    response = await async_client.post(
        "/api/verification/",
        json=verification_request,
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    
    # Check response
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "verification_id" in data
    assert "timestamp" in data
    assert data["public_key_id"] == public_key["id"]
    
    # Test retrieving verification by ID
    verification_id = data["verification_id"]
    get_response = await async_client.get(
        f"/api/verification/{verification_id}",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    
    # Check response
    assert get_response.status_code == 200
    get_data = get_response.json()
    assert get_data["verification_id"] == verification_id
    assert get_data["success"] is True


@pytest.mark.asyncio
async def test_verify_invalid_signature(async_client: AsyncClient, test_user, auth_token):
    """Test verifying an invalid digital signature."""
    # Skip test if test_user is None or doesn't have expected structure
    if not test_user or not isinstance(test_user, dict) or "id" not in test_user:
        pytest.skip("Test user not available or invalid")
        
    # Generate test key pair
    key_data = await generate_test_key_pair()
    
    # Create a test public key
    public_key = await create_test_public_key(async_client, auth_token, key_data)
    
    # Hash the document
    document_hash_raw = hashes.Hash(hashes.SHA256())
    document_hash_raw.update(test_document.encode())
    document_hash = document_hash_raw.finalize()
    document_hash_b64 = base64.b64encode(document_hash).decode('utf-8')
    
    # Create an invalid signature (random bytes)
    invalid_signature = base64.b64encode(b"invalid_signature").decode('utf-8')
    
    # Create verification request with invalid signature
    verification_request = {
        "document_hash": document_hash_b64,
        "signature": invalid_signature,
        "public_key_id": public_key["id"],
        "algorithm_name": "RSA-SHA256",
        "document_id": str(uuid.uuid4()),
        "metadata": test_metadata
    }
    
    # Make verification request
    response = await async_client.post(
        "/api/verification/",
        json=verification_request,
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    
    # Check response - should be 200 but with success=false
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is False
    assert "verification_id" in data
    assert "error" in data


@pytest.mark.asyncio
async def test_verify_no_auth(async_client: AsyncClient):
    """Test verifying a signature without authentication."""
    # Create a simple verification request
    verification_request = {
        "document_hash": "test",
        "signature": "test",
        "public_key_id": str(uuid.uuid4()),
        "algorithm_name": "RSA-SHA256"
    }
    
    # Make verification request without authentication
    response = await async_client.post(
        "/api/verification/",
        json=verification_request
    )
    
    # Check response - should be 403 Forbidden
    assert response.status_code == 403 
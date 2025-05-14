from typing import Dict, Any, Optional, List, Tuple
import base64
import binascii
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.exceptions import InvalidSignature

from src.core.interfaces import SignatureAlgorithmProvider
from src.core.registry import get_algorithm_registry


class RSAProvider(SignatureAlgorithmProvider):
    """
    RSA signature algorithm implementation.
    """
    
    def __init__(self):
        # Default supported key sizes
        self._supported_curves = {
            "RSA-2048": {
                "bit_size": 2048,
                "description": "RSA with 2048-bit key size"
            },
            "RSA-3072": {
                "bit_size": 3072,
                "description": "RSA with 3072-bit key size"
            },
            "RSA-4096": {
                "bit_size": 4096,
                "description": "RSA with 4096-bit key size"
            }
        }
        
        # Hash algorithm options
        self._hash_algorithms = {
            "SHA256": hashes.SHA256(),
            "SHA384": hashes.SHA384(),
            "SHA512": hashes.SHA512()
        }
        
        # Default hash algorithm
        self._default_hash = self._hash_algorithms["SHA256"]
        
        # Load configuration from database
        self._load_config_from_db()
    
    def _load_config_from_db(self):
        """Load configuration from the database."""
        registry = get_algorithm_registry()
        algorithm_data = registry.get_algorithm_data(self.get_algorithm_name())
        
        if not algorithm_data or "curves" not in algorithm_data:
            return
        
        # Check if a specific hash algorithm is specified
        if "hash_algorithm" in algorithm_data:
            hash_name = algorithm_data["hash_algorithm"]
            if hash_name in self._hash_algorithms:
                self._default_hash = self._hash_algorithms[hash_name]
        
        # Update supported key sizes
        for name, curve_data in algorithm_data["curves"].items():
            params = curve_data.get("parameters", {})
            
            self._supported_curves[name] = {
                "bit_size": params.get("bit_size", 2048),
                "description": curve_data.get("description", "")
            }
            
            # Check for curve-specific hash algorithm
            if "hash_algorithm" in params:
                hash_name = params["hash_algorithm"]
                if hash_name in self._hash_algorithms:
                    self._supported_curves[name]["hash_algorithm"] = self._hash_algorithms[hash_name]
    
    def get_algorithm_name(self) -> str:
        """Get the algorithm name."""
        return "RSA-SHA256"
    
    def get_algorithm_type(self) -> str:
        """Get the algorithm type."""
        return "asymmetric"
    
    def get_supported_curves(self) -> Dict[str, Dict[str, Any]]:
        """Get the supported key sizes."""
        return self._supported_curves.copy()
    
    def verify(self, document: str, signature: str, public_key: str, 
              key_size: Optional[str] = "RSA-2048", **kwargs) -> bool:
        """
        Verifies an RSA signature.
        
        Args:
            document: The document to verify (base64 encoded)
            signature: The signature (hex string)
            public_key: The public key (hex string)
            key_size: The RSA key size to use
            
        Returns:
            bool: True if signature is valid, False otherwise
        """
        try:
            # Decode the document
            document_bytes = base64.b64decode(document)
            
            # Get hash algorithm to use
            hash_algo = self._supported_curves.get(key_size, {}).get("hash_algorithm", self._default_hash)
            
            # Hash the document
            hasher = hashes.Hash(hash_algo)
            hasher.update(document_bytes)
            document_hash = hasher.finalize()
            
            # Convert signature from hex to bytes
            signature = signature.lower().strip()
            if signature.startswith('0x'):
                signature = signature[2:]
            signature_bytes = binascii.unhexlify(signature)
            
            # Convert public key from hex to bytes
            public_key = public_key.lower().strip()
            if public_key.startswith('0x'):
                public_key = public_key[2:]
            public_key_bytes = binascii.unhexlify(public_key)
            
            # Load public key
            public_key_obj = rsa.RSAPublicKey.from_public_bytes(public_key_bytes)
            
            # Use PSS padding for verification
            padding_algorithm = padding.PSS(
                mgf=padding.MGF1(hash_algo),
                salt_length=padding.PSS.MAX_LENGTH
            )
            
            # Verify signature
            public_key_obj.verify(
                signature_bytes,
                document_hash,
                padding_algorithm,
                None  # No prehashing needed
            )
            
            return True
            
        except Exception as e:
            print(f"Verification error: {e}")
            return False
    
    def sign(self, document: str, private_key: str, 
             key_size: Optional[str] = "RSA-2048", **kwargs) -> Tuple[str, str]:
        """
        Signs a document using RSA.
        
        Args:
            document: The document to sign (base64 encoded)
            private_key: The private key (hex string)
            key_size: The RSA key size to use
            
        Returns:
            Tuple[str, str]: The signature (hex string) and document hash (base64 encoded)
        """
        try:
            # Decode the document
            document_bytes = base64.b64decode(document)
            
            # Get hash algorithm to use
            hash_algo = self._supported_curves.get(key_size, {}).get("hash_algorithm", self._default_hash)
            
            # Hash the document
            hasher = hashes.Hash(hash_algo)
            hasher.update(document_bytes)
            document_hash = hasher.finalize()
            document_hash_b64 = base64.b64encode(document_hash).decode()
            
            # Convert private key from hex to bytes
            private_key = private_key.lower().strip()
            if private_key.startswith('0x'):
                private_key = private_key[2:]
            private_key_bytes = binascii.unhexlify(private_key)
            
            # Load private key
            private_key_obj = rsa.RSAPrivateKey.from_private_bytes(private_key_bytes)
            
            # Use PSS padding for signing
            padding_algorithm = padding.PSS(
                mgf=padding.MGF1(hash_algo),
                salt_length=padding.PSS.MAX_LENGTH
            )
            
            # Sign the hash
            signature_bytes = private_key_obj.sign(
                document_hash,
                padding_algorithm,
                None  # No prehashing needed
            )
            
            # Convert signature to hex
            signature_hex = binascii.hexlify(signature_bytes).decode('ascii')
            
            return signature_hex, document_hash_b64
            
        except Exception as e:
            raise ValueError(f"Signing failed: {str(e)}")
    
    def configure_from_db_data(self, db_data: Dict[str, Any]) -> None:
        """Configure the provider with data from the database."""
        if not db_data:
            return
        
        # Reload configuration
        self._load_config_from_db() 
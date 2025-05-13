from typing import Dict, Any, Optional, List
import base64
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding, rsa, utils
from cryptography.hazmat.primitives.serialization import load_pem_public_key, load_der_public_key
from cryptography.exceptions import InvalidSignature

from src.core.interfaces import SignatureAlgorithmProvider, PublicKeyValidator
from src.core.registry import get_algorithm_registry


class RSAProvider(SignatureAlgorithmProvider, PublicKeyValidator):
    """
    RSA signature algorithm implementation.
    """
    
    def __init__(self):
        # Default parameters - will be overridden by database if available
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
        
        # Use SHA-256 by default
        self._hash_algorithm = hashes.SHA256()
        
        # Load parameters from database if available
        self._load_params_from_db()
    
    def _load_params_from_db(self):
        """Load parameters from the database via registry."""
        registry = get_algorithm_registry()
        algorithm_data = registry.get_algorithm_data(self.get_algorithm_name())
        
        if not algorithm_data or "curves" not in algorithm_data:
            return
        
        # Map hash algorithm names to cryptography objects
        hash_map = {
            "SHA256": hashes.SHA256(),
            "SHA384": hashes.SHA384(),
            "SHA512": hashes.SHA512()
        }
        
        # Check if a specific hash algorithm is specified for the algorithm
        if "hash_algorithm" in algorithm_data:
            hash_name = algorithm_data["hash_algorithm"]
            if hash_name in hash_map:
                self._hash_algorithm = hash_map[hash_name]
        
        for name, curve_data in algorithm_data["curves"].items():
            params = curve_data.get("parameters", {})
            
            # Update the local curve definition
            self._supported_curves[name] = {
                "bit_size": params.get("bit_size", 2048),
                "description": curve_data.get("description", "")
            }
            
            # If this curve has a specific hash algorithm
            if "hash_algorithm" in params:
                hash_name = params["hash_algorithm"]
                if hash_name in hash_map:
                    self._supported_curves[name]["hash_algorithm"] = hash_map[hash_name]
    
    def get_algorithm_name(self) -> str:
        """Get the algorithm name."""
        return "RSA-SHA256"
    
    def get_algorithm_type(self) -> str:
        """Get the algorithm type."""
        return "asymmetric"
    
    def verify(self, document_hash: str, signature: str, public_key: str, 
              key_size: Optional[str] = "RSA-2048", **kwargs) -> bool:
        """
        Verifies an RSA signature.
        
        Args:
            document_hash (str): The hash of the document, base64 encoded
            signature (str): The signature to verify, base64 encoded
            public_key (str): The PEM or DER encoded public key
            key_size (Optional[str]): The RSA key size to use for verification
            
        Returns:
            bool: True if the signature is valid, False otherwise
        """
        try:
            # Decode the signature and hash
            signature_bytes = base64.b64decode(signature)
            hash_bytes = base64.b64decode(document_hash)
            
            # Load the public key
            try:
                public_key_obj = load_pem_public_key(public_key.encode())
            except ValueError:
                # Try DER format if PEM fails
                public_key_obj = load_der_public_key(base64.b64decode(public_key))
            
            # Use PSS padding for more security
            padding_algorithm = padding.PSS(
                mgf=padding.MGF1(self._hash_algorithm),
                salt_length=padding.PSS.MAX_LENGTH
            )
            
            # Verify the signature
            public_key_obj.verify(
                signature_bytes,
                hash_bytes,
                padding_algorithm,
                utils.Prehashed(self._hash_algorithm)
            )
            return True
        except (InvalidSignature, ValueError, TypeError) as e:
            return False
    
    def get_supported_curves(self) -> Dict[str, Dict[str, Any]]:
        """Get the supported key sizes for RSA."""
        return self._supported_curves.copy()
    
    def get_curve_parameters(self, curve_name: str) -> Dict[str, Any]:
        if curve_name not in self._supported_curves:
            raise ValueError(f"Unsupported RSA key size: {curve_name}")
        
        return self._supported_curves[curve_name].copy()
    
    def validate_public_key(self, public_key: str, curve_name: Optional[str] = None, **kwargs) -> bool:
        """
        Validates that a public key is properly formatted for RSA.
        
        Args:
            public_key (str): The public key to validate
            curve_name (Optional[str]): The key size (not strictly required for validation)
            
        Returns:
            bool: True if the public key is valid, False otherwise
        """
        try:
            # Try to load the key in PEM format
            try:
                key = load_pem_public_key(public_key.encode())
            except ValueError:
                # Try DER format if PEM fails
                key = load_der_public_key(base64.b64decode(public_key))
            
            # Check if it's an RSA key
            if not isinstance(key, rsa.RSAPublicKey):
                return False
            
            # If curve_name (key size) is specified, check if it matches
            if curve_name:
                key_size = key.key_size
                expected_size = self._supported_curves.get(curve_name, {}).get("bit_size")
                if expected_size and key_size != expected_size:
                    return False
            
            return True
        except Exception:
            return False
    
    def get_supported_formats(self) -> List[str]:
        """Get the supported key formats."""
        return ["PEM", "DER", "JWK"] 
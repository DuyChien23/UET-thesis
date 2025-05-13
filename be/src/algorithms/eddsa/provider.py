from typing import Dict, Any, Optional, List
import base64
import hashlib
from cryptography.hazmat.primitives.asymmetric import ed25519, ed448
from cryptography.hazmat.primitives.serialization import load_pem_public_key, load_der_public_key
from cryptography.exceptions import InvalidSignature

from src.core.interfaces import SignatureAlgorithmProvider, PublicKeyValidator
from src.core.registry import get_algorithm_registry


class EdDSAProvider(SignatureAlgorithmProvider, PublicKeyValidator):
    """
    EdDSA (Edwards-curve Digital Signature Algorithm) implementation.
    """
    
    def __init__(self):
        # Default curve definitions - will be overridden by database if available
        self._supported_curves = {
            "Ed25519": {
                "bit_size": 256,
                "description": "Edwards Curve 25519"
            },
            "Ed448": {
                "bit_size": 448,
                "description": "Edwards Curve 448"
            }
        }
        
        # Load curves from database if available
        self._load_curves_from_db()
    
    def _load_curves_from_db(self):
        """Load curves from the database via registry."""
        registry = get_algorithm_registry()
        algorithm_data = registry.get_algorithm_data(self.get_algorithm_name())
        
        if not algorithm_data or "curves" not in algorithm_data:
            return
        
        for name, curve_data in algorithm_data["curves"].items():
            params = curve_data.get("parameters", {})
            
            # Update the local curve definition
            self._supported_curves[name] = {
                "bit_size": params.get("bit_size", 256),
                "description": curve_data.get("description", "")
            }
    
    def get_algorithm_name(self) -> str:
        """Get the algorithm name."""
        return "EdDSA"
    
    def get_algorithm_type(self) -> str:
        """Get the algorithm type."""
        return "edwards-curve"
    
    def verify(self, document_hash: str, signature: str, public_key: str, 
              curve_name: Optional[str] = "Ed25519", **kwargs) -> bool:
        """
        Verifies an EdDSA signature.
        
        Args:
            document_hash (str): The hash of the document, base64 encoded
            signature (str): The signature to verify, base64 encoded
            public_key (str): The PEM or DER encoded public key
            curve_name (Optional[str]): The curve to use for verification
            
        Returns:
            bool: True if the signature is valid, False otherwise
        """
        if curve_name not in self._supported_curves:
            raise ValueError(f"Unsupported curve: {curve_name}")
        
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
                
            # Verify the signature
            public_key_obj.verify(signature_bytes, hash_bytes)
            return True
        except (InvalidSignature, ValueError, TypeError) as e:
            return False
    
    def get_supported_curves(self) -> Dict[str, Dict[str, Any]]:
        """Get the supported curves for this algorithm."""
        return self._supported_curves.copy()
    
    def get_curve_parameters(self, curve_name: str) -> Dict[str, Any]:
        if curve_name not in self._supported_curves:
            raise ValueError(f"Unsupported curve: {curve_name}")
        
        return self._supported_curves[curve_name].copy()
    
    def validate_public_key(self, public_key: str, curve_name: Optional[str] = None, **kwargs) -> bool:
        """
        Validates that a public key is properly formatted for EdDSA.
        
        Args:
            public_key (str): The public key to validate
            curve_name (Optional[str]): The curve name (not strictly required for validation)
            
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
            
            # Check if it's an Ed25519 or Ed448 key
            if curve_name == "Ed25519" or curve_name is None:
                return isinstance(key, ed25519.Ed25519PublicKey)
            elif curve_name == "Ed448":
                return isinstance(key, ed448.Ed448PublicKey)
            else:
                return False
        except Exception:
            return False
    
    def get_supported_formats(self) -> List[str]:
        """Get the supported key formats."""
        return ["PEM", "DER", "JWK"] 
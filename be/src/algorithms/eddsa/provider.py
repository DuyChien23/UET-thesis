from typing import Dict, Any, Optional
import base64
from cryptography.hazmat.primitives.asymmetric import ed25519, ed448
from cryptography.hazmat.primitives.serialization import load_pem_public_key, load_der_public_key
from cryptography.exceptions import InvalidSignature

from src.core.interfaces import SignatureAlgorithmProvider, PublicKeyValidator


class EdDSAProvider(SignatureAlgorithmProvider, PublicKeyValidator):
    """
    EdDSA (Edwards-curve Digital Signature Algorithm) implementation.
    """
    
    def __init__(self):
        self._supported_curves = {
            "Ed25519": {
                "key_class": ed25519.Ed25519PublicKey,
                "bit_size": 256,
                "description": "Edwards Curve 25519"
            },
            "Ed448": {
                "key_class": ed448.Ed448PublicKey,
                "bit_size": 448,
                "description": "Edwards Curve 448"
            }
        }
    
    def get_algorithm_name(self) -> str:
        return "EdDSA"
    
    def get_algorithm_type(self) -> str:
        return "EdDSA"
    
    def verify(self, document_hash: str, signature: str, public_key: str, 
               curve_name: Optional[str] = "Ed25519", **kwargs) -> bool:
        """
        Verifies an EdDSA signature.
        
        Args:
            document_hash (str): The document data (not a hash) base64 encoded - EdDSA handles hashing internally
            signature (str): The signature to verify, base64 encoded
            public_key (str): The PEM or DER encoded public key
            curve_name (Optional[str]): The curve to use for verification
            
        Returns:
            bool: True if the signature is valid, False otherwise
        """
        if curve_name not in self._supported_curves:
            raise ValueError(f"Unsupported curve: {curve_name}")
        
        try:
            # Decode the signature and message
            signature_bytes = base64.b64decode(signature)
            message_bytes = base64.b64decode(document_hash)
            
            # Load the public key
            try:
                public_key_obj = load_pem_public_key(public_key.encode())
            except ValueError:
                # Try DER format if PEM fails
                public_key_obj = load_der_public_key(base64.b64decode(public_key))
            
            # Check if the key is the expected type based on curve
            expected_class = self._supported_curves[curve_name]["key_class"]
            if not isinstance(public_key_obj, expected_class):
                return False
            
            # Verify the signature
            public_key_obj.verify(signature_bytes, message_bytes)
            return True
        except (InvalidSignature, ValueError, TypeError):
            return False
    
    def get_supported_curves(self) -> Dict[str, Dict[str, Any]]:
        return {
            name: {k: v for k, v in info.items() if k != "key_class"} 
            for name, info in self._supported_curves.items()
        }
    
    def get_curve_parameters(self, curve_name: str) -> Dict[str, Any]:
        if curve_name not in self._supported_curves:
            raise ValueError(f"Unsupported curve: {curve_name}")
        
        return {k: v for k, v in self._supported_curves[curve_name].items() if k != "key_class"}
    
    def validate_public_key(self, public_key: str, curve_name: Optional[str] = None, **kwargs) -> bool:
        """
        Validates that a public key is properly formatted for EdDSA.
        
        Args:
            public_key (str): The public key to validate
            curve_name (Optional[str]): The curve name (required for EdDSA validation)
            
        Returns:
            bool: True if the public key is valid, False otherwise
        """
        if curve_name is not None and curve_name not in self._supported_curves:
            return False
            
        try:
            # Try to load the key in PEM format
            try:
                key = load_pem_public_key(public_key.encode())
            except ValueError:
                # Try DER format if PEM fails
                key = load_der_public_key(base64.b64decode(public_key))
            
            # If curve name is specified, check if it's the right type
            if curve_name:
                expected_class = self._supported_curves[curve_name]["key_class"]
                return isinstance(key, expected_class)
            
            # Otherwise just check if it's any supported EdDSA key type
            return any(isinstance(key, info["key_class"]) for info in self._supported_curves.values())
        except Exception:
            return False
    
    def get_supported_formats(self) -> list[str]:
        return ["PEM", "DER"] 
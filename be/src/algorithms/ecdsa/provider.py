from typing import Dict, Any, Optional
import base64
import hashlib
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec, utils
from cryptography.hazmat.primitives.serialization import load_pem_public_key, load_der_public_key
from cryptography.exceptions import InvalidSignature

from core.interfaces import SignatureAlgorithmProvider, PublicKeyValidator


class ECDSAProvider(SignatureAlgorithmProvider, PublicKeyValidator):
    """
    ECDSA (Elliptic Curve Digital Signature Algorithm) implementation.
    """
    
    def __init__(self):
        self._supported_curves = {
            "secp256r1": {
                "curve_class": ec.SECP256R1,
                "hash_algorithm": hashes.SHA256(),
                "bit_size": 256,
                "description": "NIST P-256 curve (also known as prime256v1)"
            },
            "secp384r1": {
                "curve_class": ec.SECP384R1,
                "hash_algorithm": hashes.SHA384(),
                "bit_size": 384,
                "description": "NIST P-384 curve"
            },
            "secp521r1": {
                "curve_class": ec.SECP521R1,
                "hash_algorithm": hashes.SHA512(),
                "bit_size": 521,
                "description": "NIST P-521 curve"
            }
        }
    
    def get_algorithm_name(self) -> str:
        return "ECDSA"
    
    def get_algorithm_type(self) -> str:
        return "ECDSA"
    
    def verify(self, document_hash: str, signature: str, public_key: str, 
               curve_name: Optional[str] = "secp256r1", **kwargs) -> bool:
        """
        Verifies an ECDSA signature.
        
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
            curve_info = self._supported_curves[curve_name]
            public_key_obj.verify(
                signature_bytes,
                hash_bytes,
                ec.ECDSA(utils.Prehashed(curve_info["hash_algorithm"]))
            )
            return True
        except (InvalidSignature, ValueError, TypeError) as e:
            return False
    
    def get_supported_curves(self) -> Dict[str, Dict[str, Any]]:
        return {
            name: {k: v for k, v in info.items() if k != "curve_class"} 
            for name, info in self._supported_curves.items()
        }
    
    def get_curve_parameters(self, curve_name: str) -> Dict[str, Any]:
        if curve_name not in self._supported_curves:
            raise ValueError(f"Unsupported curve: {curve_name}")
        
        return {k: v for k, v in self._supported_curves[curve_name].items() if k != "curve_class"}
    
    def validate_public_key(self, public_key: str, curve_name: Optional[str] = None, **kwargs) -> bool:
        """
        Validates that a public key is properly formatted for ECDSA.
        
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
            
            # Check if it's an EC key
            return isinstance(key, ec.EllipticCurvePublicKey)
        except Exception:
            return False
    
    def get_supported_formats(self) -> list[str]:
        return ["PEM", "DER"] 
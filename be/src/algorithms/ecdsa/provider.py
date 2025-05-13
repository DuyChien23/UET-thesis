from typing import Dict, Any, Optional, List
import base64
import hashlib
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec, utils
from cryptography.hazmat.primitives.serialization import load_pem_public_key, load_der_public_key
from cryptography.exceptions import InvalidSignature

from src.core.interfaces import SignatureAlgorithmProvider, PublicKeyValidator
from src.core.registry import get_algorithm_registry


class ECDSAProvider(SignatureAlgorithmProvider, PublicKeyValidator):
    """
    ECDSA (Elliptic Curve Digital Signature Algorithm) implementation.
    """
    
    def __init__(self):
        # Default curve definitions - will be overridden by database if available
        self._supported_curves = {
            "secp256k1": {
                "curve_class": ec.SECP256K1,
                "hash_algorithm": hashes.SHA256(),
                "bit_size": 256,
                "description": "SECG curve used in Bitcoin and blockchain applications"
            },
            "secp256r1": {
                "curve_class": ec.SECP256R1,
                "hash_algorithm": hashes.SHA256(),
                "bit_size": 256,
                "description": "NIST curve P-256, widely used for general purpose applications"
            },
            "secp384r1": {
                "curve_class": ec.SECP384R1,
                "hash_algorithm": hashes.SHA384(),
                "bit_size": 384,
                "description": "NIST curve P-384, for higher security requirements"
            },
            "secp521r1": {
                "curve_class": ec.SECP521R1,
                "hash_algorithm": hashes.SHA512(),
                "bit_size": 521,
                "description": "NIST curve P-521, for very high security requirements"
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
        
        # Map hash algorithm names to cryptography objects
        hash_map = {
            "SHA256": hashes.SHA256(),
            "SHA384": hashes.SHA384(),
            "SHA512": hashes.SHA512()
        }
        
        # Map curve names to cryptography curve classes
        curve_class_map = {
            "secp256k1": ec.SECP256K1,
            "secp256r1": ec.SECP256R1,
            "secp384r1": ec.SECP384R1,
            "secp521r1": ec.SECP521R1
        }
        
        for name, curve_data in algorithm_data["curves"].items():
            params = curve_data.get("parameters", {})
            bit_size = params.get("bit_size", 256)
            
            # Determine hash algorithm based on bit size or explicit name
            hash_algo_name = params.get("hash_algorithm", "")
            if hash_algo_name and hash_algo_name in hash_map:
                hash_algo = hash_map[hash_algo_name]
            elif bit_size <= 256:
                hash_algo = hashes.SHA256()
            elif bit_size <= 384:
                hash_algo = hashes.SHA384()
            else:
                hash_algo = hashes.SHA512()
            
            # Get the curve class from the map or default to secp256r1
            curve_class = curve_class_map.get(name, ec.SECP256R1)
            
            # Update the local curve definition
            self._supported_curves[name] = {
                "curve_class": curve_class,
                "hash_algorithm": hash_algo,
                "bit_size": bit_size,
                "description": curve_data.get("description", "")
            }
    
    def get_algorithm_name(self) -> str:
        """Get the algorithm name."""
        return "ECDSA"
    
    def get_algorithm_type(self) -> str:
        """Get the algorithm type."""
        return "elliptic-curve"
    
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
        """Get the supported curves for this algorithm."""
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
    
    def get_supported_formats(self) -> List[str]:
        """Get the supported key formats."""
        return ["PEM", "DER", "JWK"] 
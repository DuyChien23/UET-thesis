from typing import Dict, Any, Optional
import base64
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding, rsa, utils
from cryptography.hazmat.primitives.serialization import load_pem_public_key, load_der_public_key
from cryptography.exceptions import InvalidSignature

from src.core.interfaces import SignatureAlgorithmProvider, PublicKeyValidator


class RSAProvider(SignatureAlgorithmProvider, PublicKeyValidator):
    """
    RSA digital signature algorithm implementation.
    """
    
    def __init__(self):
        self._supported_padding_schemes = {
            "PKCS1v15": {
                "padding_class": padding.PKCS1v15(),
                "description": "PKCS#1 v1.5 padding scheme"
            },
            "PSS-SHA256": {
                "padding_class": padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                "hash_algorithm": hashes.SHA256(),
                "description": "Probabilistic Signature Scheme with SHA-256"
            },
            "PSS-SHA384": {
                "padding_class": padding.PSS(
                    mgf=padding.MGF1(hashes.SHA384()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                "hash_algorithm": hashes.SHA384(),
                "description": "Probabilistic Signature Scheme with SHA-384"
            },
            "PSS-SHA512": {
                "padding_class": padding.PSS(
                    mgf=padding.MGF1(hashes.SHA512()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                "hash_algorithm": hashes.SHA512(),
                "description": "Probabilistic Signature Scheme with SHA-512"
            }
        }
        
        self._supported_key_sizes = [2048, 3072, 4096]
    
    def get_algorithm_name(self) -> str:
        return "RSA"
    
    def get_algorithm_type(self) -> str:
        return "RSA"
    
    def verify(self, document_hash: str, signature: str, public_key: str, 
               curve_name: Optional[str] = None, **kwargs) -> bool:
        """
        Verifies an RSA signature.
        
        Args:
            document_hash (str): The hash of the document, base64 encoded
            signature (str): The signature to verify, base64 encoded
            public_key (str): The PEM or DER encoded public key
            curve_name (Optional[str]): Not used for RSA
            **kwargs: Additional parameters such as padding_scheme
            
        Returns:
            bool: True if the signature is valid, False otherwise
        """
        padding_scheme = kwargs.get("padding_scheme", "PKCS1v15")
        
        if padding_scheme not in self._supported_padding_schemes:
            raise ValueError(f"Unsupported padding scheme: {padding_scheme}")
        
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
            
            # Check if it's an RSA key
            if not isinstance(public_key_obj, rsa.RSAPublicKey):
                return False
                
            # Get the padding scheme configuration
            padding_info = self._supported_padding_schemes[padding_scheme]
            padding_obj = padding_info["padding_class"]
            
            # If using PSS, we need to specify the hash algorithm
            if padding_scheme.startswith("PSS-"):
                hash_algorithm = padding_info["hash_algorithm"]
                public_key_obj.verify(
                    signature_bytes,
                    hash_bytes,
                    padding_obj,
                    utils.Prehashed(hash_algorithm)
                )
            else:
                # For PKCS1v15, we don't need to specify the hash algorithm for verification
                public_key_obj.verify(
                    signature_bytes,
                    hash_bytes,
                    padding_obj
                )
            return True
        except (InvalidSignature, ValueError, TypeError) as e:
            return False
    
    def get_supported_curves(self) -> Dict[str, Dict[str, Any]]:
        # RSA doesn't use curves, but we'll return the padding schemes
        return {
            name: {k: v for k, v in info.items() if k != "padding_class"} 
            for name, info in self._supported_padding_schemes.items()
        }
    
    def get_curve_parameters(self, curve_name: str) -> Dict[str, Any]:
        # Reuse this method for padding schemes in RSA
        if curve_name not in self._supported_padding_schemes:
            raise ValueError(f"Unsupported padding scheme: {curve_name}")
        
        return {k: v for k, v in self._supported_padding_schemes[curve_name].items() if k != "padding_class"}
    
    def validate_public_key(self, public_key: str, curve_name: Optional[str] = None, **kwargs) -> bool:
        """
        Validates that a public key is properly formatted for RSA.
        
        Args:
            public_key (str): The public key to validate
            curve_name (Optional[str]): Not used for RSA
            **kwargs: Additional parameters such as min_key_size
            
        Returns:
            bool: True if the public key is valid, False otherwise
        """
        min_key_size = kwargs.get("min_key_size", 2048)
        
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
                
            # Check key size
            key_size = key.key_size
            return key_size >= min_key_size
        except Exception:
            return False
    
    def get_supported_formats(self) -> list[str]:
        return ["PEM", "DER"] 
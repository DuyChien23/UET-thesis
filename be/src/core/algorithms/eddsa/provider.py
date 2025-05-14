from typing import Dict, Any, Optional, List, Tuple
import base64
import binascii
from cryptography.hazmat.primitives.asymmetric import ed25519, ed448
from cryptography.exceptions import InvalidSignature

from src.core.interfaces import SignatureAlgorithmProvider
from src.core.registry import get_algorithm_registry


class EdDSAProvider(SignatureAlgorithmProvider):
    """
    EdDSA (Edwards-curve Digital Signature Algorithm) implementation.
    """
    
    def __init__(self):
        self._supported_curves = {}
        self._load_curves_from_db()
    
    def _load_curves_from_db(self):
        """Load curves from the database via registry."""
        registry = get_algorithm_registry()
        algorithm_data = registry.get_algorithm_data(self.get_algorithm_name())
        
        if not algorithm_data or "curves" not in algorithm_data:
            return
        
        for name, curve_data in algorithm_data["curves"].items():
            if name not in self._supported_curves:
                continue
                
            params = curve_data.get("parameters", {})
            
            # Update the local curve definition
            self._supported_curves[name] = {
                "description": curve_data.get("description", ""),
                "bit_size": params.get("bit_size", 256 if name == "Ed25519" else 448)
            }
    
    def get_algorithm_name(self) -> str:
        """Get the algorithm name."""
        return "EdDSA"
    
    def get_algorithm_type(self) -> str:
        """Get the algorithm type."""
        return "edwards-curve"
    
    def get_supported_curves(self) -> Dict[str, Dict[str, Any]]:
        """Get the supported curves for this algorithm."""
        return self._supported_curves.copy()
    
    def verify(self, document: str, signature: str, public_key: str, 
               curve_name: Optional[str] = "Ed25519", **kwargs) -> bool:
        """
        Verifies an EdDSA signature.
        
        Args:
            document: The document to verify (base64 encoded)
            signature: The signature to verify (hex string)
            public_key: The public key (hex string)
            curve_name: The curve to use (Ed25519 or Ed448)
            
        Returns:
            bool: True if the signature is valid, False otherwise
        """
        if curve_name not in self._supported_curves:
            raise ValueError(f"Unsupported curve: {curve_name}")
        
        try:
            # Decode the document
            document_bytes = base64.b64decode(document)
            
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
            
            # Create verifier
            if curve_name == "Ed25519":
                verifier = ed25519.Ed25519PublicKey.from_public_bytes(public_key_bytes)
            elif curve_name == "Ed448":
                verifier = ed448.Ed448PublicKey.from_public_bytes(public_key_bytes)
            else:
                return False
                    
            # Verify the signature
            verifier.verify(signature_bytes, document_bytes)
            return True
            
        except Exception as e:
            print(f"Verification error: {e}")
            return False
    
    def sign(self, document: str, private_key: str, curve_name: Optional[str] = "Ed25519", 
            **kwargs) -> Tuple[str, str]:
        """
        Signs a document using EdDSA.
        
        Args:
            document: The document to sign (base64 encoded)
            private_key: The private key (hex string)
            curve_name: The curve to use (Ed25519 or Ed448)
            
        Returns:
            Tuple[str, str]: The signature (hex string) and the document (base64 encoded)
        """
        if curve_name not in self._supported_curves:
            raise ValueError(f"Unsupported curve: {curve_name}")
        
        try:
            # Decode the document
            document_bytes = base64.b64decode(document)
            
            # Convert private key from hex to bytes
            private_key = private_key.lower().strip()
            if private_key.startswith('0x'):
                private_key = private_key[2:]
            private_key_bytes = binascii.unhexlify(private_key)
            
            # Create signer
            if curve_name == "Ed25519":
                signer = ed25519.Ed25519PrivateKey.from_private_bytes(private_key_bytes)
            elif curve_name == "Ed448":
                signer = ed448.Ed448PrivateKey.from_private_bytes(private_key_bytes)
            else:
                raise ValueError(f"Unsupported curve: {curve_name}")
            
            # Sign the document
            signature_bytes = signer.sign(document_bytes)
            
            # Convert signature to hex
            signature_hex = binascii.hexlify(signature_bytes).decode('ascii')
            
            # Return the signature and original document
            return signature_hex, document
            
        except Exception as e:
            raise ValueError(f"Signing failed: {str(e)}")
    
    def configure_from_db_data(self, db_data: Dict[str, Any]) -> None:
        """Configure the provider with data from the database."""
        if not db_data or "curves" not in db_data:
            return
        
        # Reload the curves
        self._load_curves_from_db() 
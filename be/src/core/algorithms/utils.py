"""
Utility functions for handling digital signatures.
"""

import base64
from typing import Union, Tuple


def encode_signature(signature: Union[bytes, str]) -> str:
    """
    Encode a signature to a base64 string.
    
    Args:
        signature: The signature as bytes or string
        
    Returns:
        Base64-encoded string representation of the signature
    """
    if isinstance(signature, str):
        # If it's already a string, check if it's already base64 encoded
        try:
            base64.b64decode(signature)
            return signature  # It's already a valid base64 string
        except Exception:
            # Encode string to bytes then to base64
            return base64.b64encode(signature.encode('utf-8')).decode('ascii')
    else:
        # It's bytes, encode to base64
        return base64.b64encode(signature).decode('ascii')


def decode_signature(signature: str) -> bytes:
    """
    Decode a base64-encoded signature string to bytes.
    
    Args:
        signature: Base64-encoded signature string
        
    Returns:
        Decoded signature as bytes
        
    Raises:
        ValueError: If the signature is not a valid base64 string
    """
    try:
        return base64.b64decode(signature)
    except Exception as e:
        raise ValueError(f"Invalid base64-encoded signature: {e}") 
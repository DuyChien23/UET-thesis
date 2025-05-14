"""
Core interfaces for the application.
Defines the interfaces that must be implemented by various components.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Tuple


class SignatureAlgorithmProvider(ABC):
    """
    Interface for signature algorithm providers.
    Each provider represents a signature algorithm like ECDSA, RSA, etc.
    This interface must be implemented by all algorithm providers.
    """
    
    @abstractmethod
    def get_algorithm_name(self) -> str:
        """
        Get the name of the algorithm.
        
        Returns:
            str: The algorithm name
        """
        pass
    
    @abstractmethod
    def verify(self, document: str, signature: str, public_key: str, 
               curve_name: Optional[str] = None, **kwargs) -> bool:
        """
        Verify a signature.
        
        Args:
            document: The document to verify, base64 encoded
            signature: The signature to verify, base64 encoded
            public_key: The PEM or DER encoded public key
            curve_name: The curve or key type to use
            **kwargs: Additional parameters specific to the algorithm
            
        Returns:
            bool: True if the signature is valid, False otherwise
        """
        pass
    
    @abstractmethod
    def sign(self, document: str, private_key: str, curve_name: Optional[str] = None, 
            **kwargs) -> Tuple[str, str]:
        """
        Sign a document.
        
        Args:
            document: The document to sign, base64 encoded
            private_key: The PEM or DER encoded private key
            curve_name: The curve or key type to use
            **kwargs: Additional parameters specific to the algorithm
            
        Returns:
            Tuple[str, str]: The signature (base64 encoded) and the hash of the document (base64 encoded)
        """
        pass




class CurveProvider(ABC):
    """
    Interface for providing curve-specific operations.
    """
    
    @abstractmethod
    def get_curve_name(self) -> str:
        """
        Returns the name of the curve.
        
        Returns:
            str: The curve name
        """
        pass
    
    @abstractmethod
    def get_curve_parameters(self) -> Dict[str, Any]:
        """
        Returns the parameters of the curve.
        
        Returns:
            Dict[str, Any]: Dictionary of curve parameters
        """
        pass
    

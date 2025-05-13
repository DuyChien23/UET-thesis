"""
Core interfaces for the application.
Defines the interfaces that must be implemented by various components.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional


class SignatureAlgorithmProvider(ABC):
    """
    Interface for signature algorithm providers.
    Each provider represents a signature algorithm like ECDSA, RSA, etc.
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
    def get_algorithm_type(self) -> str:
        """
        Get the type of the algorithm.
        
        Returns:
            str: The algorithm type
        """
        pass
    
    @abstractmethod
    def get_supported_curves(self) -> Dict[str, Dict[str, Any]]:
        """
        Get the supported curves or key types for this algorithm.
        
        Returns:
            Dict[str, Dict[str, Any]]: A dictionary mapping curve names to their properties
        """
        pass
    
    def get_supported_formats(self) -> List[str]:
        """
        Get the supported key formats for this algorithm.
        
        Returns:
            List[str]: A list of supported key formats
        """
        return ["PEM", "DER"]  # Default formats
    
    @abstractmethod
    def verify(self, data_hash: bytes, signature: bytes, public_key: bytes, 
               curve_name: str = None) -> bool:
        """
        Verify a signature.
        
        Args:
            data_hash (bytes): The hash of the data that was signed
            signature (bytes): The signature to verify
            public_key (bytes): The public key to use for verification
            curve_name (str, optional): The curve or key type to use
            
        Returns:
            bool: True if the signature is valid, False otherwise
        """
        pass


class PublicKeyValidator(ABC):
    """
    Interface for validating public keys for a specific algorithm.
    """
    
    @abstractmethod
    def validate_public_key(self, 
                           public_key: str, 
                           curve_name: Optional[str] = None, 
                           **kwargs) -> bool:
        """
        Validates that a public key is properly formatted and valid for this algorithm.
        
        Args:
            public_key (str): The public key to validate
            curve_name (Optional[str]): The curve name for elliptic curve algorithms
            **kwargs: Additional parameters specific to the algorithm
            
        Returns:
            bool: True if the public key is valid, False otherwise
        """
        pass
    
    @abstractmethod
    def get_supported_formats(self) -> list[str]:
        """
        Returns the public key formats supported by this validator.
        
        Returns:
            list[str]: List of supported formats (e.g., PEM, DER, raw)
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
    
    @abstractmethod
    def is_valid_public_key(self, public_key: str) -> bool:
        """
        Checks if a public key is valid for this curve.
        
        Args:
            public_key (str): The public key to check
            
        Returns:
            bool: True if the public key is valid for this curve, False otherwise
        """
        pass 
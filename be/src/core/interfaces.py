from abc import ABC, abstractmethod
from typing import Dict, Any, Optional


class SignatureAlgorithmProvider(ABC):
    """
    Abstract interface for signature algorithm providers.
    All algorithm implementations should inherit from this interface.
    """
    
    @abstractmethod
    def get_algorithm_name(self) -> str:
        """
        Returns the name of the algorithm.
        
        Returns:
            str: The algorithm name
        """
        pass
    
    @abstractmethod
    def get_algorithm_type(self) -> str:
        """
        Returns the type of the algorithm (e.g., ECDSA, RSA, EdDSA).
        
        Returns:
            str: The algorithm type
        """
        pass
    
    @abstractmethod
    def verify(self, 
               document_hash: str, 
               signature: str, 
               public_key: str, 
               curve_name: Optional[str] = None, 
               **kwargs) -> bool:
        """
        Verifies a signature using this algorithm.
        
        Args:
            document_hash (str): The hash of the document that was signed
            signature (str): The signature to verify
            public_key (str): The public key to use for verification
            curve_name (Optional[str]): The curve name for elliptic curve algorithms
            **kwargs: Additional parameters specific to the algorithm
            
        Returns:
            bool: True if the signature is valid, False otherwise
        """
        pass
    
    @abstractmethod
    def get_supported_curves(self) -> Dict[str, Dict[str, Any]]:
        """
        Returns the curves supported by this algorithm, if applicable.
        
        Returns:
            Dict[str, Dict[str, Any]]: Dictionary of curve names to their parameters
        """
        pass
    
    @abstractmethod
    def get_curve_parameters(self, curve_name: str) -> Dict[str, Any]:
        """
        Returns the parameters for a specific curve.
        
        Args:
            curve_name (str): The name of the curve
            
        Returns:
            Dict[str, Any]: Dictionary of curve parameters
            
        Raises:
            ValueError: If the curve is not supported
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
from typing import Dict, Optional, List, Type
from .interfaces import SignatureAlgorithmProvider
import logging
from threading import Lock

logger = logging.getLogger(__name__)


class AlgorithmRegistry:
    """
    Registry for signature algorithm providers.
    Implements the Singleton pattern to ensure only one registry exists.
    """
    _instance = None
    _lock: Lock = Lock()
    
    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(AlgorithmRegistry, cls).__new__(cls)
                cls._instance._algorithms: Dict[str, SignatureAlgorithmProvider] = {}
                cls._instance._default_algorithm: Optional[str] = None
            return cls._instance
    
    def register_algorithm(self, provider: SignatureAlgorithmProvider) -> None:
        """
        Register a new algorithm provider in the registry.
        
        Args:
            provider (SignatureAlgorithmProvider): The algorithm provider to register
            
        Raises:
            ValueError: If an algorithm with the same name is already registered
        """
        algorithm_name = provider.get_algorithm_name()
        if algorithm_name in self._algorithms:
            raise ValueError(f"Algorithm '{algorithm_name}' is already registered")
        
        self._algorithms[algorithm_name] = provider
        logger.info(f"Registered algorithm provider: {algorithm_name}")
        
        # If this is the first algorithm registered, make it the default
        if self._default_algorithm is None:
            self._default_algorithm = algorithm_name
            logger.info(f"Set default algorithm to: {algorithm_name}")
    
    def unregister_algorithm(self, algorithm_name: str) -> None:
        """
        Unregister an algorithm provider from the registry.
        
        Args:
            algorithm_name (str): The name of the algorithm to unregister
            
        Raises:
            KeyError: If the algorithm is not registered
        """
        if algorithm_name not in self._algorithms:
            raise KeyError(f"Algorithm '{algorithm_name}' is not registered")
        
        # If we're removing the default algorithm, reset it
        if self._default_algorithm == algorithm_name:
            self._default_algorithm = next(iter(self._algorithms.keys())) if self._algorithms else None
            
        del self._algorithms[algorithm_name]
        logger.info(f"Unregistered algorithm provider: {algorithm_name}")
    
    def get_algorithm(self, algorithm_name: str) -> SignatureAlgorithmProvider:
        """
        Get an algorithm provider by name.
        
        Args:
            algorithm_name (str): The name of the algorithm
            
        Returns:
            SignatureAlgorithmProvider: The algorithm provider
            
        Raises:
            KeyError: If the algorithm is not registered
        """
        if algorithm_name not in self._algorithms:
            raise KeyError(f"Algorithm '{algorithm_name}' is not registered")
        
        return self._algorithms[algorithm_name]
    
    def get_default_algorithm(self) -> Optional[SignatureAlgorithmProvider]:
        """
        Get the default algorithm provider.
        
        Returns:
            Optional[SignatureAlgorithmProvider]: The default algorithm provider,
            or None if no algorithms are registered
        """
        if self._default_algorithm is None:
            return None
        
        return self._algorithms[self._default_algorithm]
    
    def set_default_algorithm(self, algorithm_name: str) -> None:
        """
        Set the default algorithm.
        
        Args:
            algorithm_name (str): The name of the algorithm to set as default
            
        Raises:
            KeyError: If the algorithm is not registered
        """
        if algorithm_name not in self._algorithms:
            raise KeyError(f"Algorithm '{algorithm_name}' is not registered")
        
        self._default_algorithm = algorithm_name
        logger.info(f"Set default algorithm to: {algorithm_name}")
    
    def get_registered_algorithms(self) -> List[str]:
        """
        Get a list of all registered algorithm names.
        
        Returns:
            List[str]: A list of all registered algorithm names
        """
        return list(self._algorithms.keys())
    
    def get_algorithm_providers(self) -> Dict[str, SignatureAlgorithmProvider]:
        """
        Get a dictionary of all registered algorithm providers.
        
        Returns:
            Dict[str, SignatureAlgorithmProvider]: A dictionary mapping algorithm names to providers
        """
        return self._algorithms.copy()


# Factory function to get the singleton instance
def get_algorithm_registry() -> AlgorithmRegistry:
    """
    Get the singleton instance of the algorithm registry.
    
    Returns:
        AlgorithmRegistry: The singleton instance
    """
    return AlgorithmRegistry()


def get_algorithm_provider(algorithm_name: str) -> Optional[SignatureAlgorithmProvider]:
    """
    Get an algorithm provider by name.
    
    This is a convenience function to get a provider from the registry without
    having to handle the KeyError exception.
    
    Args:
        algorithm_name (str): The name of the algorithm
        
    Returns:
        Optional[SignatureAlgorithmProvider]: The algorithm provider, 
        or None if the algorithm is not registered
    """
    registry = get_algorithm_registry()
    try:
        return registry.get_algorithm(algorithm_name)
    except KeyError:
        logger.warning(f"Algorithm provider '{algorithm_name}' not found")
        return None 
from typing import Dict, Optional, List, Type, Union, Any
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
                cls._instance._algorithms = {}
                cls._instance._default_algorithm = None
                cls._instance._loaded_db_data = {}
            return cls._instance
    
    @property
    def providers(self) -> Dict[str, SignatureAlgorithmProvider]:
        """Get all registered algorithm providers."""
        return self._algorithms.copy()
    
    @property
    def db_data(self) -> Dict[str, Dict]:
        """Get the database data for all algorithms."""
        return self._loaded_db_data
    
    def set_db_data(self, data: Dict[str, Dict]) -> None:
        """
        Set the database data for the algorithms.
        
        Args:
            data: Dictionary with algorithm data from the database
        """
        self._loaded_db_data = data
        logger.info(f"Loaded data for {len(data)} algorithms from database")
        
        # Update all providers with the database data
        for algorithm_name, algorithm_data in data.items():
            if algorithm_name in self._algorithms:
                provider = self._algorithms[algorithm_name]
                try:
                    provider.configure_from_db_data(algorithm_data)
                    logger.info(f"Configured provider {algorithm_name} with database data")
                except Exception as e:
                    logger.error(f"Failed to configure provider {algorithm_name}: {e}")
    
    def register(self, algorithm_name: str, provider: SignatureAlgorithmProvider) -> None:
        """
        Register a new algorithm provider in the registry.
        
        Args:
            algorithm_name: The name of the algorithm
            provider: The algorithm provider to register
            
        Raises:
            ValueError: If an algorithm with the same name is already registered
        """
        if algorithm_name in self._algorithms:
            logger.warning(f"Algorithm '{algorithm_name}' is already registered, replacing")
            
        self._algorithms[algorithm_name] = provider
        logger.info(f"Registered algorithm provider: {algorithm_name}")
        
        # If this is the first algorithm registered, make it the default
        if self._default_algorithm is None:
            self._default_algorithm = algorithm_name
            logger.info(f"Set default algorithm to: {algorithm_name}")
            
        # If we have database data for this algorithm, configure the provider
        if algorithm_name in self._loaded_db_data:
            try:
                provider.configure_from_db_data(self._loaded_db_data[algorithm_name])
                logger.info(f"Configured provider {algorithm_name} with database data")
            except Exception as e:
                logger.error(f"Failed to configure provider {algorithm_name}: {e}")
    
    def register_algorithm(self, provider: SignatureAlgorithmProvider) -> None:
        """
        Register a new algorithm provider in the registry using its name.
        
        Args:
            provider: The algorithm provider to register
            
        Raises:
            ValueError: If an algorithm with the same name is already registered
        """
        algorithm_name = provider.get_algorithm_name()
        self.register(algorithm_name, provider)
    
    def unregister_algorithm(self, algorithm_name: str) -> None:
        """
        Unregister an algorithm provider from the registry.
        
        Args:
            algorithm_name: The name of the algorithm to unregister
            
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
            algorithm_name: The name of the algorithm
            
        Returns:
            The algorithm provider
            
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
            The default algorithm provider, or None if no algorithms are registered
        """
        if self._default_algorithm is None:
            return None
        
        return self._algorithms[self._default_algorithm]
    
    def set_default_algorithm(self, algorithm_name: str) -> None:
        """
        Set the default algorithm.
        
        Args:
            algorithm_name: The name of the algorithm to set as default
            
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
            A list of all registered algorithm names
        """
        return list(self._algorithms.keys())
    
    def get_algorithm_providers(self) -> Dict[str, SignatureAlgorithmProvider]:
        """
        Get a dictionary of all registered algorithm providers.
        
        Returns:
            A dictionary mapping algorithm names to providers
        """
        return self._algorithms.copy()
    
    def get_algorithm_data(self, algorithm_name: str) -> Optional[Dict]:
        """
        Get the database data for an algorithm.
        
        Args:
            algorithm_name: The name of the algorithm
            
        Returns:
            The algorithm data from the database, or None if not found
        """
        return self._loaded_db_data.get(algorithm_name)
    
    def get_curve_data(self, algorithm_name: str, curve_name: str) -> Optional[Dict]:
        """
        Get the database data for a curve.
        
        Args:
            algorithm_name: The name of the algorithm
            curve_name: The name of the curve
            
        Returns:
            The curve data from the database, or None if not found
        """
        algorithm_data = self.get_algorithm_data(algorithm_name)
        if not algorithm_data or "curves" not in algorithm_data:
            return None
        
        return algorithm_data["curves"].get(curve_name)
    
    def get_all_algorithms(self) -> Dict[str, Dict[str, Any]]:
        """
        Get all algorithm data in a structured format.
        
        Returns:
            A dictionary mapping algorithm names to their data
        """
        result = {}
        
        for algorithm_name, provider in self._algorithms.items():
            try:
                supported_curves = provider.get_supported_curves()
                
                # Get algorithm data from the database
                db_data = self.get_algorithm_data(algorithm_name) or {}
                
                # Create the algorithm data
                algorithm_data = {
                    "name": algorithm_name,
                    "type": provider.get_algorithm_type(),
                    "description": db_data.get("description", ""),
                    "curves": supported_curves
                }
                
                result[algorithm_name] = algorithm_data
            except Exception as e:
                logger.error(f"Error getting data for algorithm {algorithm_name}: {e}")
        
        return result
    
    def find_algorithm_for_curve(self, curve_name: str) -> Optional[Dict[str, Any]]:
        """
        Find the algorithm that supports a specific curve.
        
        Args:
            curve_name: The name of the curve
            
        Returns:
            The algorithm data, or None if no algorithm supports this curve
        """
        for algorithm_name, provider in self._algorithms.items():
            try:
                supported_curves = provider.get_supported_curves()
                if curve_name in supported_curves:
                    return {
                        "name": algorithm_name,
                        "provider": provider,
                        "curve_data": supported_curves[curve_name]
                    }
            except Exception as e:
                logger.error(f"Error checking curve support for algorithm {algorithm_name}: {e}")
        
        return None


# Factory function to get the singleton instance
def get_algorithm_registry() -> AlgorithmRegistry:
    """
    Get the singleton instance of the algorithm registry.
    
    Returns:
        The singleton instance
    """
    return AlgorithmRegistry()


def get_algorithm_provider(algorithm_name: str) -> Optional[SignatureAlgorithmProvider]:
    """
    Get an algorithm provider by name.
    
    This is a convenience function to get a provider from the registry without
    having to handle the KeyError exception.
    
    Args:
        algorithm_name: The name of the algorithm
        
    Returns:
        The algorithm provider, or None if the algorithm is not registered
    """
    registry = get_algorithm_registry()
    try:
        return registry.get_algorithm(algorithm_name)
    except KeyError:
        logger.warning(f"Algorithm provider '{algorithm_name}' not found")
        return None


def find_algorithm_for_curve(curve_name: str) -> Optional[Dict[str, Any]]:
    """
    Find the algorithm that supports a specific curve.
    
    This is a convenience function to find an algorithm by curve name.
    
    Args:
        curve_name: The name of the curve
        
    Returns:
        The algorithm data, or None if no algorithm supports this curve
    """
    registry = get_algorithm_registry()
    return registry.find_algorithm_for_curve(curve_name) 
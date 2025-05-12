"""
Digital signature algorithm initialization module.
This module imports and registers all available algorithm providers.
"""

from src.core.registry import get_algorithm_registry
from src.algorithms.ecdsa.provider import ECDSAProvider
from src.algorithms.eddsa.provider import EdDSAProvider
from src.algorithms.rsa.provider import RSAProvider

def initialize_algorithms():
    """
    Initialize and register all available signature algorithm providers.
    """
    registry = get_algorithm_registry()
    
    # Register ECDSA
    registry.register_algorithm(ECDSAProvider())
    
    # Register EdDSA
    registry.register_algorithm(EdDSAProvider())
    
    # Register RSA
    registry.register_algorithm(RSAProvider())
    
    # Set ECDSA as the default
    registry.set_default_algorithm("ECDSA") 
"""
Signing service module.
Provides functionality for signing documents using various cryptographic algorithms.
"""

import uuid
import base64
import hashlib
import logging
from typing import Dict, Any, Optional, Tuple
from datetime import datetime

from src.core.registry import get_algorithm_registry, find_algorithm_for_curve
from src.services.algorithms import AlgorithmService

logger = logging.getLogger(__name__)


class SigningService:
    """
    Service for signing documents.
    """
    
    def __init__(self, algorithm_service: Optional[AlgorithmService] = None):
        """
        Initialize the signing service.
        
        Args:
            algorithm_service: Algorithm service for fetching algorithm data
        """
        self.algorithm_service = algorithm_service
        self.algorithm_registry = get_algorithm_registry()
        
    async def sign_document(
        self,
        document: str,
        private_key: str,
        curve_name: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Sign a document using the specified private key and curve.
        
        Args:
            document: Base64 encoded document to sign
            private_key: Base64 encoded private key
            curve_name: Name of the curve to use
            metadata: Additional metadata for the signing
            
        Returns:
            Dict with signature, document hash, and public key
        """
        try:
            # Find the algorithm for this curve
            algorithm_data = find_algorithm_for_curve(curve_name)
            if not algorithm_data:
                raise ValueError(f"No algorithm found for curve: {curve_name}")
            
            algorithm_name = algorithm_data["name"]
            provider = algorithm_data["provider"]
        
            
            # Sign the document using the provider
            logger.info(f"Signing document with algorithm {algorithm_name} and curve {curve_name}")
            signature, document_hash, public_key = provider.sign(document, private_key, curve_name)
            
            # Return the result
            return {
                "signature": signature,
                "document_hash": document_hash,
                "signing_time": datetime.utcnow(),
                "public_key": public_key
            }
        except Exception as e:
            logger.error(f"Signing failed: {str(e)}")
            raise ValueError(f"Signing failed: {str(e)}")
    
    async def verify_signature(
        self,
        document_hash: str,
        signature: str,
        algorithm_name: str,
        public_key: str,
        curve_name: Optional[str] = None
    ) -> bool:
        """
        Verify a signature.
        
        Args:
            document_hash: Base64 encoded hash of the document
            signature: Base64 encoded signature
            algorithm_name: Name of the algorithm to use
            public_key: Base64 encoded public key
            curve_name: Name of the curve to use (optional)
            
        Returns:
            True if the signature is valid, False otherwise
        """
        try:
            # Get the algorithm provider
            provider = self.algorithm_registry.get_algorithm(algorithm_name)
            
            # Verify the signature
            return provider.verify(document_hash, signature, public_key, curve_name)
        except Exception as e:
            logger.error(f"Verification failed: {str(e)}")
            return False
            
    async def list_supported_algorithms(self) -> Dict[str, Any]:
        """
        Get information about all supported algorithms and curves.
        
        Returns:
            Information about all supported algorithms
        """
        return self.algorithm_registry.get_all_algorithms()
        
    async def get_algorithm_for_curve(self, curve_name: str) -> Dict[str, Any]:
        """
        Get the algorithm that supports a specific curve.
        
        Args:
            curve_name: Name of the curve
            
        Returns:
            Information about the algorithm
            
        Raises:
            ValueError: If no algorithm supports this curve
        """
        algorithm_data = find_algorithm_for_curve(curve_name)
        if not algorithm_data:
            raise ValueError(f"No algorithm found for curve: {curve_name}")
        
        return {
            "name": algorithm_data["name"],
            "type": algorithm_data["provider"].get_algorithm_type(),
            "curve_data": algorithm_data["curve_data"]
        } 
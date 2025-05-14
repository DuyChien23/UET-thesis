"""
Signing service module.
Provides functionality for signing documents using various cryptographic algorithms.
"""

import uuid
import base64
import hashlib
import logging
from typing import Dict, Any, Optional
from datetime import datetime

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec, utils, padding, rsa, ed25519
from cryptography.hazmat.primitives.serialization import load_pem_private_key, load_der_private_key

from src.core.registry import get_algorithm_registry
from src.db.repositories.algorithms import AlgorithmRepository, CurveRepository
from src.db.repositories.verification import VerificationRepository
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
            Dict with signature and metadata
        """
        try:
            # Determine the algorithm to use based on the curve name
            algorithm_data = await self._get_algorithm_for_curve(curve_name)
            algorithm_name = algorithm_data["name"]
            
            # Hash the document
            document_bytes = base64.b64decode(document)
            
            # Generate a unique ID for this signing
            signing_id = str(uuid.uuid4())
            
            # Sign the document based on the algorithm type
            signature, algorithm_used = await self._sign_with_algorithm(
                document_bytes,
                private_key,
                algorithm_name,
                curve_name
            )
            
            # Return the result
            return {
                "id": signing_id,
                "document": document,
                "signature": base64.b64encode(signature).decode(),
                "algorithm_name": algorithm_used,
                "curve_name": curve_name,
                "signing_time": datetime.utcnow(),
                "metadata": metadata
            }
        except Exception as e:
            logger.error(f"Signing failed: {str(e)}")
            raise ValueError(f"Signing failed: {str(e)}")
            
    async def _get_algorithm_for_curve(self, curve_name: str) -> Dict[str, Any]:
        """
        Determine the appropriate algorithm for a given curve.
        
        Args:
            curve_name: Name of the curve
            
        Returns:
            Algorithm data
        """
        # Get all algorithms from the registry
        for algo_name, algo_data in self.algorithm_registry.get_all_algorithms().items():
            if "curves" in algo_data and curve_name in algo_data["curves"]:
                return {
                    "name": algo_name,
                    "type": algo_data["type"],
                    "curve_data": algo_data["curves"][curve_name]
                }
        
        raise ValueError(f"No algorithm found for curve: {curve_name}")
    
    async def _sign_with_algorithm(
        self,
        document_bytes: bytes,
        private_key_b64: str,
        algorithm_name: str,
        curve_name: str
    ) -> tuple[bytes, str]:
        """
        Sign document bytes using the specified algorithm.
        
        Args:
            document_bytes: Document bytes to sign
            private_key_b64: Base64 encoded private key
            algorithm_name: Name of the algorithm to use
            curve_name: Name of the curve to use
            
        Returns:
            tuple[bytes, str]: Signature bytes and algorithm name used
        """
        # First, try to decode the private key
        try:
            # Try PEM format first
            private_key_bytes = base64.b64decode(private_key_b64)
            try:
                private_key = load_pem_private_key(private_key_bytes, password=None)
            except ValueError:
                # Try DER format if PEM fails
                private_key = load_der_private_key(private_key_bytes, password=None)
        except Exception as e:
            raise ValueError(f"Invalid private key format: {str(e)}")
        
        # Use the appropriate signing method based on algorithm
        if algorithm_name == "ECDSA":
            # For ECDSA, hash the document with the appropriate hash algorithm
            if curve_name in ["secp256r1", "secp256k1"]:
                hash_algorithm = hashes.SHA256()
            elif curve_name == "secp384r1":
                hash_algorithm = hashes.SHA384()
            else:  # secp521r1 or others
                hash_algorithm = hashes.SHA512()
                
            # Hash the document
            hasher = hashlib.new(hash_algorithm.name)
            hasher.update(document_bytes)
            document_hash = hasher.digest()
            
            # Sign the hash
            signature = private_key.sign(
                document_hash,
                ec.ECDSA(utils.Prehashed(hash_algorithm))
            )
            return signature, algorithm_name
            
        elif algorithm_name == "RSA-SHA256":
            # For RSA, use the PKCS#1 v1.5 padding
            signature = private_key.sign(
                document_bytes,
                padding.PKCS1v15(),
                hashes.SHA256()
            )
            return signature, algorithm_name
            
        elif algorithm_name == "EdDSA":
            # For EdDSA (Ed25519), sign directly
            if isinstance(private_key, ed25519.Ed25519PrivateKey):
                signature = private_key.sign(document_bytes)
                return signature, algorithm_name
            else:
                raise ValueError("Invalid private key type for EdDSA")
                
        else:
            raise ValueError(f"Unsupported algorithm: {algorithm_name}") 
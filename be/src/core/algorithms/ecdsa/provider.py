from typing import Dict, Any, Optional, List, Tuple
import base64
import hashlib
import random
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec, utils
from cryptography.hazmat.primitives.serialization import (
    load_pem_public_key, load_der_public_key,
    load_pem_private_key, load_der_private_key
)
from cryptography.exceptions import InvalidSignature

from src.core.interfaces import SignatureAlgorithmProvider, CurveProvider
from src.core.registry import get_algorithm_registry


class ECDSAProvider(SignatureAlgorithmProvider):
    """
    ECDSA (Elliptic Curve Digital Signature Algorithm) implementation.
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
            params = curve_data.get("parameters", {})
            bit_size = params.get("bit_size", 256)
 
            hash_map = {
                "SHA256": hashes.SHA256(),
                "SHA384": hashes.SHA384(),
                "SHA512": hashes.SHA512()
            }
            
            # Determine hash algorithm based on bit size or explicit name
            hash_algo_name = params.get("hash_algorithm", "")
            if hash_algo_name and hash_algo_name in hash_map:
                hash_algo = hash_map[hash_algo_name]
            elif bit_size <= 256:
                hash_algo = hashes.SHA256()
            elif bit_size <= 384:
                hash_algo = hashes.SHA384()
            else:
                hash_algo = hashes.SHA512()

            ecdsaCurve = ECDSACurveProvider(name, params)
            
            # Update the local curve definition
            self._supported_curves[name] = {
                "curve": ecdsaCurve,
                "hash_algorithm": hash_algo,
                "bit_size": bit_size,
                "description": curve_data.get("description", "")
            }

    
    def get_algorithm_name(self) -> str:
        """Get the algorithm name."""
        return "ECDSA"
    
    def get_algorithm_type(self) -> str:
        """Get the algorithm type."""
        return "elliptic-curve"
    
    def get_supported_curves(self) -> Dict[str, Dict[str, Any]]:
        """
        Get the supported curves for this algorithm.
        
        Returns:
            Dict[str, Dict[str, Any]]: Dictionary of supported curves and their parameters
        """
        result = {}
        for name, curve_data in self._supported_curves.items():
            result[name] = {
                "bit_size": curve_data["bit_size"],
                "description": curve_data["description"],
                "parameters": curve_data["curve"].get_curve_parameters()
            }
        return result
    
    def verify(self, document: str, signature: str, public_key: str, 
               curve_name: Optional[str] = "secp256r1", **kwargs) -> bool:
        """
        Verifies an ECDSA signature.
        
        Args:
            document: document (base64 encoded)
            signature: The signature value (hex string)
            public_key: public key value (hex string)
            curve_name: The curve to use for verification
            
        Returns:
            bool: True if the signature is valid, False otherwise
        """
        if curve_name not in self._supported_curves:
            raise ValueError(f"Unsupported curve: {curve_name}")
        
        try:
            # Decode the document
            document_bytes = base64.b64decode(document)
            
            # Get the curve info and hash algorithm
            curve_info = self._supported_curves[curve_name]
            hash_algorithm = curve_info["hash_algorithm"]
            
            # Hash the document
            hasher = hashlib.new(hash_algorithm.name)
            hasher.update(document_bytes)
            document_hash = hasher.digest()
            
            # Convert document hash to integer
            hash_int = int.from_bytes(document_hash, byteorder='big')
            
            # Convert signature from hex to integer
            signature = signature.lower().strip()
            if signature.startswith('0x'):
                signature = signature[2:]
            signature_int = int(signature, 16)
            
            # Convert public key from hex to integer
            public_key = public_key.lower().strip()
            if public_key.startswith('0x'):
                public_key = public_key[2:]
            public_key_int = int(public_key, 16)
            
            # Use our curve provider to verify
            return curve_info["curve"].verify(hash_int, signature_int, public_key_int)
                
        except Exception as e:
            print(f"Verification error: {e}")
            return False
    
    def sign(self, document: str, private_key: str, curve_name: Optional[str] = "secp256r1", 
            **kwargs) -> Tuple[str, str]:
        """
        Signs a document using ECDSA.
        
        Args:
            document: document (base64 encoded)
            private_key: private key value (hex string)
            curve_name: curve to use for signing
            
        Returns:
            Tuple[str, str]: The signature (hex string) and the hash of the document (base64 encoded)
        """
        if curve_name not in self._supported_curves:
            raise ValueError(f"Unsupported curve: {curve_name}")
        
        try:
            # Decode the document
            document_bytes = base64.b64decode(document)
            
            # Get the curve info and hash algorithm
            curve_info = self._supported_curves[curve_name]
            hash_algorithm = curve_info["hash_algorithm"]
            
            # Hash the document
            hasher = hashlib.new(hash_algorithm.name)
            hasher.update(document_bytes)
            document_hash = hasher.digest()
            document_hash_b64 = base64.b64encode(document_hash).decode()
            
            # Convert document hash to integer
            hash_int = int.from_bytes(document_hash, byteorder='big')
            
            # Convert private key from hex to integer
            private_key = private_key.lower().strip()
            if private_key.startswith('0x'):
                private_key = private_key[2:]
            priv_key_int = int(private_key, 16)
            
            # Sign with our curve provider
            signature_int = curve_info["curve"].sign(hash_int, priv_key_int)
            
            # Convert signature to hex string
            signature_hex = format(signature_int, 'x')
            if len(signature_hex) % 2 == 1:
                signature_hex = '0' + signature_hex
            
            return signature_hex, document_hash_b64
                
        except Exception as e:
            raise ValueError(f"Signing failed: {e}")
    
    def configure_from_db_data(self, db_data: Dict[str, Any]) -> None:
        """
        Configure the provider with data from the database.
        
        Args:
            db_data: Database data for this algorithm
        """
        if not db_data or "curves" not in db_data:
            return
        
        # Reload the curves
        self._load_curves_from_db()


class ECDSACurveProvider(CurveProvider):
    """
    ECDSA curve provider implementation.
    """
    
    def __init__(self, curve_name: str, parameters: Dict[str, Any]):
        self._curve_name = curve_name

        if "p" not in parameters:
            raise ValueError("p is required")
        if "a" not in parameters:
            raise ValueError("a is required")
        if "b" not in parameters:
            raise ValueError("b is required")
        if "n" not in parameters:
            raise ValueError("n is required")
        if "g" not in parameters:
            raise ValueError("g is required")
        
        self._parameters = parameters
        
        # Parse the curve parameters
        self._p = self._parse_int_param(parameters["p"])
        self._a = self._parse_int_param(parameters["a"])
        self._b = self._parse_int_param(parameters["b"])
        self._n = self._parse_int_param(parameters["n"])
        
        # Parse the generator point
        self._g = self._parse_point_param(parameters["g"])
    
    def _parse_int_param(self, param) -> int:
        """Parse an integer parameter from various formats."""
        if isinstance(param, int):
            return param
        elif isinstance(param, str):
            if param.startswith("0x"):
                return int(param, 16)
            else:
                return int(param)
        else:
            raise ValueError(f"Invalid parameter format: {param}")
    
    def _parse_point_param(self, param) -> Tuple[int, int]:
        """Parse a point parameter from various formats."""
        if isinstance(param, (list, tuple)) and len(param) == 2:
            return (self._parse_int_param(param[0]), self._parse_int_param(param[1]))
        elif isinstance(param, dict) and "x" in param and "y" in param:
            return (self._parse_int_param(param["x"]), self._parse_int_param(param["y"]))
        elif isinstance(param, str):
            # Try to parse string formats like "0xXX,0xYY" or "x,y"
            parts = param.split(",")
            if len(parts) == 2:
                x_str = parts[0].strip()
                y_str = parts[1].strip()
                return (self._parse_int_param(x_str), self._parse_int_param(y_str))
        
        raise ValueError(f"Invalid point format: {param}")

    def get_curve_name(self) -> str:
        return self._curve_name
    
    def get_curve_parameters(self) -> Dict[str, Any]:
        return self._parameters
    
    def _point_add(self, p: Tuple[int, int], q: Tuple[int, int]) -> Tuple[int, int]:
        """
        Add two points on the elliptic curve.
        """
        # Handle point at infinity
        if p is None:
            return q
        if q is None:
            return p
        
        x1, y1 = p
        x2, y2 = q
        
        # Check if the points are the same
        if x1 == x2 and y1 == y2:
            # Point doubling
            # Calculate lambda = (3x₁² + a) / 2y₁
            numerator = (3 * x1 * x1 + self._a) % self._p
            denominator = (2 * y1) % self._p
            
            # Calculate modular inverse
            lambda_val = (numerator * pow(denominator, self._p - 2, self._p)) % self._p
        elif x1 == x2:
            # Points are on a vertical line, result is the point at infinity
            return None
        else:
            # Point addition
            # Calculate lambda = (y₂ - y₁) / (x₂ - x₁)
            numerator = (y2 - y1) % self._p
            denominator = (x2 - x1) % self._p
            
            # Calculate modular inverse
            lambda_val = (numerator * pow(denominator, self._p - 2, self._p)) % self._p
        
        # Calculate the new point
        # x₃ = λ² - x₁ - x₂
        x3 = (lambda_val * lambda_val - x1 - x2) % self._p
        
        # y₃ = λ(x₁ - x₃) - y₁
        y3 = (lambda_val * (x1 - x3) - y1) % self._p
        
        return (x3, y3)

    def _scalar_mult(self, k: int, p: Tuple[int, int]) -> Tuple[int, int]:
        """
        Perform scalar multiplication on an elliptic curve point.
        """
        # Handle special cases
        if k == 0 or p is None:
            return None  # Point at infinity
        
        if k == 1:
            return p
            
        if k < 0:
            # Negation: reflection across x-axis
            k = -k
            p = (p[0], (-p[1]) % self._p)
        
        # Double-and-add algorithm
        result = None  # Start with the point at infinity
        addend = p
        
        # Process each bit of k
        while k > 0:
            if k & 1:  # LSB is set
                result = self._point_add(result, addend)
            
            # Double the addend
            addend = self._point_add(addend, addend)
            
            # Shift right (move to next bit)
            k >>= 1
        
        return result
    
    def sign(self, message: int, private_key: int) -> int:
        """
        Sign a message using ECDSA.
        
        Args:
            message: The message to sign
            private_key: The private key to use for signing
        """
        # Validate private key
        if not 1 <= private_key < self._n:
            raise ValueError("Private key out of range")
        
        # ECDSA signing algorithm
        while True:
            # Generate a random k value (RFC 6979 would be more secure)
            k = random.randint(1, self._n - 1)
            
            # Calculate R = k·G
            R = self._scalar_mult(k, self._g)
            if R is None:
                continue  # Try again with different k
            
            # Extract r, the x-coordinate of R
            r = R[0] % self._n
            if r == 0:
                continue  # r cannot be 0
            
            # Calculate s = k⁻¹(message + r·privateKey) mod n
            k_inv = pow(k, self._n - 2, self._n)  # Fermat's little theorem
            s = (k_inv * (message + r * private_key % self._n)) % self._n
            
            if s == 0:
                continue  # s cannot be 0
            
            # Encode the signature as a single integer: (r << bits) | s
            # where bits is enough to hold n
            n_bits = self._n.bit_length()
            signature = (r << n_bits) | s
            
            return signature

    def verify(self, message: int, signature: int, public_key: int) -> bool:
        """
        Verify a message using ECDSA.
        """
        # Decode the public key
        # If public_key is a single integer, split it into x and y coordinates
        n_bits = self._n.bit_length()
        
        if isinstance(public_key, int):
            x = public_key >> n_bits
            y = public_key & ((1 << n_bits) - 1)
            Q = (x, y)
        else:
            raise ValueError("Unsupported public key format")
        
        # Extract r and s from the signature
        r = signature >> n_bits
        s = signature & ((1 << n_bits) - 1)
        
        # Check if r and s are in the valid range
        if not (1 <= r < self._n and 1 <= s < self._n):
            return False
        
        # Calculate w = s⁻¹ mod n
        w = pow(s, self._n - 2, self._n)
        
        # Calculate u₁ = message·w mod n
        u1 = (message * w) % self._n
        
        # Calculate u₂ = r·w mod n
        u2 = (r * w) % self._n
        
        # Calculate the point P = u₁·G + u₂·Q
        point1 = self._scalar_mult(u1, self._g)
        point2 = self._scalar_mult(u2, Q)
        P = self._point_add(point1, point2)
        
        # If P is the point at infinity, the signature is invalid
        if P is None:
            return False
        
        # The signature is valid if x-coordinate of P mod n equals r
        return (P[0] % self._n) == r
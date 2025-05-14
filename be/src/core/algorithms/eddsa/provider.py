from typing import Dict, Any, Optional, Tuple
import hashlib
import random
from src.core.interfaces import SignatureAlgorithmProvider, CurveProvider
from src.core.registry import get_algorithm_registry

class EdDSAProvider(SignatureAlgorithmProvider):
    """
    EdDSA (Edwards-curve Digital Signature Algorithm) implementation.
    """
    def __init__(self):
        self._supported_curves = {}
        self._load_curves_from_db()

    def _load_curves_from_db(self):
        registry = get_algorithm_registry()
        algorithm_data = registry.get_algorithm_data(self.get_algorithm_name())
        if not algorithm_data or "curves" not in algorithm_data:
            return
        for name, curve_data in algorithm_data["curves"].items():
            params = curve_data.get("parameters", {})
            bit_size = params.get("bit_size", 256)
            hash_map = {
                "SHA256": hashlib.sha256(),
                "SHA384": hashlib.sha384(),
                "SHA512": hashlib.sha512()
            }
            hash_algo_name = params.get("hash_algorithm", "")
            if hash_algo_name and hash_algo_name in hash_map:
                hash_algo = hash_map[hash_algo_name]
            elif bit_size <= 256:
                hash_algo = hashlib.sha256()
            elif bit_size <= 384:
                hash_algo = hashlib.sha384()
            else:
                hash_algo = hashlib.sha512()
            eddsa_curve = EdDSACurveProvider(name, params)
            self._supported_curves[name] = {
                "curve": eddsa_curve,
                "hash_algorithm": hash_algo,
                "bit_size": bit_size,
                "description": curve_data.get("description", "")
            }

    def get_algorithm_name(self) -> str:
        return "EdDSA"

    def get_algorithm_type(self) -> str:
        return "edwards-curve"

    def get_supported_curves(self) -> Dict[str, Dict[str, Any]]:
        result = {}
        for name, curve_data in self._supported_curves.items():
            result[name] = {
                "bit_size": curve_data["bit_size"],
                "description": curve_data["description"],
                "parameters": curve_data["curve"].get_curve_parameters()
            }
        return result

    def verify(self, document: str, signature: str, public_key: str, curve_name: Optional[str] = "ed25519", **kwargs) -> Tuple[bool, Dict[str, Any]]:
        if curve_name not in self._supported_curves:
            raise ValueError(f"Unsupported curve: {curve_name}")
        try:
            curve_info = self._supported_curves[curve_name]
            signature = signature.lower().strip()
            if signature.startswith('0x'):
                signature = signature[2:]
            signature_int = int(signature, 16)
            public_key = public_key.lower().strip()
            if public_key.startswith('0x'):
                public_key = public_key[2:]
            public_key_int = int(public_key, 16)
            meta_data = {
                "document": document,
                "public_key": public_key,
                "curve_name": curve_name,
                "bit_size": curve_info["bit_size"]
            }
            return curve_info["curve"].verify(int(document, 16), signature_int, public_key_int), meta_data
        except Exception as e:
            print(f"Verification error: {e}")
            return False, {"error": str(e)}

    def sign(self, document: str, private_key: str, curve_name: Optional[str] = "ed25519", **kwargs) -> Tuple[str, str, str]:
        if curve_name not in self._supported_curves:
            raise ValueError(f"Unsupported curve: {curve_name}")
        try:
            curve_info = self._supported_curves[curve_name]
            private_key = private_key.lower().strip()
            if private_key.startswith('0x'):
                private_key = private_key[2:]
            priv_key_int = int(private_key, 16)
            signature_int, public_key_int = curve_info["curve"].sign(int(document, 16), priv_key_int)
            signature_hex = format(signature_int, 'x')
            public_key_hex = format(public_key_int, 'x')
            return signature_hex, document, public_key_hex
        except Exception as e:
            raise ValueError(f"Signing failed: {e}")

    def configure_from_db_data(self, db_data: Dict[str, Any]) -> None:
        if not db_data or "curves" not in db_data:
            return
        self._load_curves_from_db()

class EdDSACurveProvider(CurveProvider):
    def __init__(self, curve_name: str, parameters: Dict[str, Any]):
        self._curve_name = curve_name
        required_params = ["p", "a", "d", "g", "n", "h"]
        for param in required_params:
            if param not in parameters:
                raise ValueError(f"{param} is required for EdDSA curve")
        self._parameters = parameters
        self._p = self._parse_int_param(parameters["p"])
        self._a = self._parse_int_param(parameters["a"])
        self._d = self._parse_int_param(parameters["d"])
        self._n = self._parse_int_param(parameters["n"])
        self._h = self._parse_int_param(parameters["h"])
        self._g = self._parse_point_param(parameters["g"])
    def _parse_int_param(self, param) -> int:
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
        if isinstance(param, (list, tuple)) and len(param) == 2:
            return (self._parse_int_param(param[0]), self._parse_int_param(param[1]))
        elif isinstance(param, str):
            parts = param.replace('(','').replace(')','').split(',')
            if len(parts) == 2:
                return (self._parse_int_param(parts[0]), self._parse_int_param(parts[1]))
        raise ValueError(f"Invalid point format: {param}")
    def get_curve_name(self) -> str:
        return self._curve_name
    def get_curve_parameters(self) -> Dict[str, Any]:
        return self._parameters
    def _edwards_add(self, P: Tuple[int, int], Q: Tuple[int, int]) -> Tuple[int, int]:
        if P is None:
            return Q
        if Q is None:
            return P
        x1, y1 = P
        x2, y2 = Q
        p = self._p
        d = self._d
        a = self._a
        x1y2 = (x1 * y2) % p
        y1x2 = (y1 * x2) % p
        x1x2 = (x1 * x2) % p
        y1y2 = (y1 * y2) % p
        dx1x2y1y2 = (d * x1x2 * y1y2) % p
        denom_x = (1 + dx1x2y1y2) % p
        denom_y = (1 - dx1x2y1y2) % p
        x3 = ((x1y2 + y1x2) * pow(denom_x, p - 2, p)) % p
        y3 = ((y1y2 - a * x1x2) * pow(denom_y, p - 2, p)) % p
        return (x3, y3)
    def _scalar_mult(self, k: int, P: Tuple[int, int]) -> Tuple[int, int]:
        if k == 0 or P is None:
            return None
        if k == 1:
            return P
        if k < 0:
            k = -k
            P = (P[0], (-P[1]) % self._p)
        result = None
        addend = P
        while k > 0:
            if k & 1:
                result = self._edwards_add(result, addend)
            addend = self._edwards_add(addend, addend)
            k >>= 1
        return result
    def _compress_point(self, x: int, y: int) -> int:
        sign_bit = 1 if x & 1 else 0
        return (sign_bit << 255) | y
    def _decompress_point(self, compressed: int) -> Tuple[int, int]:
        sign_bit = (compressed >> 255) & 1
        y = compressed & ((1 << 255) - 1)
        y_squared = pow(y, 2, self._p)
        numerator = (y_squared - 1) % self._p
        denominator = (1 + self._d * y_squared) % self._p
        x_squared = (numerator * pow(denominator, self._p - 2, self._p)) % self._p
        x = pow(x_squared, (self._p + 1) // 4, self._p)
        if (x & 1) != sign_bit:
            x = self._p - x
        return (x, y)
    def sign(self, message: int, private_key: int) -> Tuple[int, int]:
        # Simple deterministic nonce for demo, not secure for production
        r = (private_key + message) % self._n
        R = self._scalar_mult(r, self._g)
        compressed_R = self._compress_point(R[0], R[1])
        A = self._scalar_mult(private_key, self._g)
        compressed_A = self._compress_point(A[0], A[1])
        k = (compressed_R + compressed_A + message) % self._n
        s = (r + k * private_key) % self._n
        signature = (compressed_R << 256) | s
        return signature, compressed_A
    def verify(self, message: int, signature: int, public_key: int) -> bool:
        compressed_R = signature >> 256
        s = signature & ((1 << 256) - 1)
        R = self._decompress_point(compressed_R)
        A = self._decompress_point(public_key)
        k = (compressed_R + public_key + message) % self._n
        sG = self._scalar_mult(s, self._g)
        R_plus_kA = self._edwards_add(R, self._scalar_mult(k, A))
        return sG == R_plus_kA

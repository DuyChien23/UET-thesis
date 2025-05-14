/**
 * Crypto utilities for document signing
 */

// Map of curve names to their default bit sizes (fallback if not provided by API)
const DEFAULT_CURVE_BIT_SIZES: Record<string, number> = {
  'secp256k1': 256,
  'secp256r1': 256, 
  'P-256': 256,
  'P-384': 384,
  'P-521': 521,
  'ed25519': 256,
  'rsa-2048': 2048,
  'rsa-4096': 4096,
};

// Map of curve names to their hash algorithms (fallback if not provided by API)
const DEFAULT_HASH_ALGORITHMS: Record<string, string> = {
  'secp256k1': 'SHA-256',
  'secp256r1': 'SHA-256',
  'P-256': 'SHA-256',
  'P-384': 'SHA-384',
  'P-521': 'SHA-512',
  'ed25519': 'SHA-512',
  'rsa-2048': 'SHA-256',
  'rsa-4096': 'SHA-256',
};

/**
 * Determines the appropriate hash algorithm based on curve parameters or defaults
 */
function getHashAlgorithmForCurve(curveName: string, curveParameters?: any): string {
  // Use curve parameters if provided by the API
  if (curveParameters && curveParameters.hash_algorithm) {
    const hashAlgo = curveParameters.hash_algorithm;
    // Convert to Web Crypto API format
    return hashAlgo.replace('SHA', 'SHA-');
  }
  
  // Fallback to defaults
  return DEFAULT_HASH_ALGORITHMS[curveName] || 'SHA-256';
}

/**
 * Converts an ArrayBuffer to a Base64 string
 */
function arrayBufferToBase64(buffer: ArrayBuffer): string {
  const bytes = new Uint8Array(buffer);
  let binary = '';
  for (let i = 0; i < bytes.byteLength; i++) {
    binary += String.fromCharCode(bytes[i]);
  }
  return btoa(binary);
}

/**
 * Converts a hash buffer to a decimal integer string
 * This ensures the hash is in the proper format for signing
 */
function hashToDecimalString(buffer: ArrayBuffer): string {
  const hashArray = Array.from(new Uint8Array(buffer));
  const bigIntValue = BigInt('0x' + hashArray.map(b => b.toString(16).padStart(2, '0')).join(''));
  return bigIntValue.toString();
}

/**
 * Hashes a document using the appropriate algorithm for the given curve
 * @param document The document to hash
 * @param curveName The name of the curve being used
 * @param curveParameters Optional curve parameters
 * @param asInteger Whether to return the hash as a decimal integer string
 * @returns The document hash as either a base64 string or decimal integer string
 */
export async function calculateDocumentHash(
  document: string, 
  curveName: string, 
  curveParameters?: any,
  asInteger: boolean = true
): Promise<string> {
  const hashAlgorithm = getHashAlgorithmForCurve(curveName, curveParameters);
  console.log(`Hashing document using algorithm: ${hashAlgorithm} for curve: ${curveName}`);
  
  // Convert the document string to a Uint8Array
  const encoder = new TextEncoder();
  const data = encoder.encode(document);
  
  // Hash the document using the Web Crypto API
  const hashBuffer = await crypto.subtle.digest(hashAlgorithm, data);
  
  // Convert the hash to either base64 or decimal integer string based on asInteger parameter
  return asInteger ? hashToDecimalString(hashBuffer) : arrayBufferToBase64(hashBuffer);
} 
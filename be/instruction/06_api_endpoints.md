# API Endpoints

## Authentication and Authorization

1. **User Authentication**
   - `POST /api/auth/register`
     - Register a new user account
     - Request: `{ "username": "string", "email": "string", "password": "string" }`
     - Response: `{ "user_id": "uuid", "username": "string", "email": "string", "created_at": "datetime" }`

   - `POST /api/auth/login`
     - Authenticate and receive a JWT access token
     - Request: `{ "username": "string", "password": "string" }`
     - Response: `{ "access_token": "string", "token_type": "bearer", "expires_in": 3600, "user": { "id": "uuid", "username": "string", "email": "string" } }`

   - `POST /api/auth/logout`
     - Add current token to blacklist in Redis
     - Headers: Authorization: Bearer {access_token}
     - Response: `{ "message": "Successfully logged out" }`

2. **User Management**
   - `GET /api/users`
     - List all users (admin only)
     - Headers: Authorization: Bearer {access_token}
     - Parameters: page, limit, status (active|inactive|suspended)
     - Response: `{ "users": [{"id": "uuid", "username": "string", "email": "string", "status": "string", "created_at": "datetime"}], "total": 100, "page": 1, "limit": 20 }`

   - `GET /api/users/{user_id}`
     - Get user details (admin or self)
     - Headers: Authorization: Bearer {access_token}
     - Response: `{ "id": "uuid", "username": "string", "email": "string", "status": "string", "created_at": "datetime", "last_login": "datetime" }`

   - `PUT /api/users/{user_id}`
     - Update user details (admin or self)
     - Headers: Authorization: Bearer {access_token}
     - Request: `{ "email": "string", "password": "string" }`
     - Response: `{ "id": "uuid", "username": "string", "email": "string", "updated_at": "datetime" }`

   - `PATCH /api/users/{user_id}/status`
     - Update user status (admin only)
     - Headers: Authorization: Bearer {access_token}
     - Request: `{ "status": "active|inactive|suspended" }`
     - Response: `{ "id": "uuid", "username": "string", "status": "string", "updated_at": "datetime" }`

3. **Role Management**
   - `GET /api/roles`
     - List all roles (admin only)
     - Headers: Authorization: Bearer {access_token}
     - Response: `{ "roles": [{"id": "uuid", "name": "string", "description": "string"}] }`

   - `GET /api/roles/{role_id}`
     - Get role details with permissions (admin only)
     - Headers: Authorization: Bearer {access_token}
     - Response: `{ "id": "uuid", "name": "string", "description": "string", "permissions": [{"id": "uuid", "name": "string", "description": "string"}] }`

   - `POST /api/roles`
     - Create a new role (admin only)
     - Headers: Authorization: Bearer {access_token}
     - Request: `{ "name": "string", "description": "string", "permissions": ["uuid"] }`
     - Response: `{ "id": "uuid", "name": "string", "description": "string" }`

   - `PUT /api/roles/{role_id}`
     - Update a role (admin only)
     - Headers: Authorization: Bearer {access_token}
     - Request: `{ "name": "string", "description": "string" }`
     - Response: `{ "id": "uuid", "name": "string", "description": "string" }`

   - `GET /api/users/{user_id}/roles`
     - Get roles for a user (admin or self)
     - Headers: Authorization: Bearer {access_token}
     - Response: `{ "user_id": "uuid", "roles": [{"id": "uuid", "name": "string", "description": "string"}] }`

   - `POST /api/users/{user_id}/roles`
     - Assign role to user (admin only)
     - Headers: Authorization: Bearer {access_token}
     - Request: `{ "role_id": "uuid" }`
     - Response: `{ "user_id": "uuid", "role_id": "uuid", "created_at": "datetime" }`

   - `DELETE /api/users/{user_id}/roles/{role_id}`
     - Remove role from user (admin only)
     - Headers: Authorization: Bearer {access_token}
     - Response: `{ "message": "Role successfully removed from user" }`

4. **Permissions**
   - `GET /api/permissions`
     - List all permissions (admin only)
     - Headers: Authorization: Bearer {access_token}
     - Response: `{ "permissions": [{"id": "uuid", "name": "string", "description": "string"}] }`

   - `GET /api/roles/{role_id}/permissions`
     - List permissions for a role (admin only)
     - Headers: Authorization: Bearer {access_token}
     - Response: `{ "role_id": "uuid", "permissions": [{"id": "uuid", "name": "string", "description": "string"}] }`

   - `POST /api/roles/{role_id}/permissions`
     - Add permission to role (admin only)
     - Headers: Authorization: Bearer {access_token}
     - Request: `{ "permission_id": "uuid" }`
     - Response: `{ "role_id": "uuid", "permission_id": "uuid", "created_at": "datetime" }`

   - `DELETE /api/roles/{role_id}/permissions/{permission_id}`
     - Remove permission from role (admin only)
     - Headers: Authorization: Bearer {access_token}
     - Response: `{ "message": "Permission successfully removed from role" }`

## Algorithm Management

1. **Algorithms**
   - `GET /api/algorithms`
     - List all supported algorithms
     - Headers: Authorization: Bearer {access_token}
     - Response: `{ "algorithms": [{"id": "uuid", "name": "string", "type": "string", "description": "string"}] }`

   - `GET /api/algorithms/{algorithm_id}`
     - Get details for a specific algorithm
     - Headers: Authorization: Bearer {access_token}
     - Response: `{ "id": "uuid", "name": "string", "type": "ECDSA|RSA|EdDSA|other", "description": "string", "created_at": "datetime" }`

   - `POST /api/algorithms`
     - Add a new algorithm (admin only)
     - Headers: Authorization: Bearer {access_token}
     - Request: `{ "name": "string", "type": "ECDSA|RSA|EdDSA|other", "description": "string" }`
     - Response: `{ "id": "uuid", "name": "string", "type": "string", "description": "string", "created_at": "datetime" }`

   - `PUT /api/algorithms/{algorithm_id}`
     - Update an algorithm (admin only)
     - Headers: Authorization: Bearer {access_token}
     - Request: `{ "name": "string", "type": "ECDSA|RSA|EdDSA|other", "description": "string" }`
     - Response: `{ "id": "uuid", "name": "string", "type": "string", "description": "string" }`

2. **Curve Management**
   - `GET /api/curves`
     - List all available elliptic curves
     - Headers: Authorization: Bearer {access_token}
     - Parameters: algorithm_id (optional), status (enabled|disabled)
     - Response: `{ "curves": [{"id": "uuid", "name": "string", "algorithm_id": "uuid", "algorithm_name": "string", "status": "enabled|disabled"}] }`

   - `GET /api/curves/{curve_id}`
     - Get details for a specific curve
     - Headers: Authorization: Bearer {access_token}
     - Response: `{ "id": "uuid", "name": "string", "algorithm_id": "uuid", "algorithm_name": "string", "parameters": {...}, "description": "string", "status": "enabled|disabled", "created_at": "datetime" }`

   - `POST /api/curves` (admin only)
     - Register a new curve
     - Headers: Authorization: Bearer {access_token}
     - Request: `{ "name": "string", "algorithm_id": "uuid", "parameters": {...}, "description": "string" }`
     - Response: `{ "id": "uuid", "name": "string", "algorithm_id": "uuid", "parameters": {...}, "description": "string", "status": "enabled", "created_at": "datetime" }`

   - `PUT /api/curves/{curve_id}` (admin only)
     - Update a curve configuration
     - Headers: Authorization: Bearer {access_token}
     - Request: `{ "name": "string", "parameters": {...}, "description": "string", "status": "enabled|disabled" }`
     - Response: `{ "id": "uuid", "name": "string", "algorithm_id": "uuid", "parameters": {...}, "description": "string", "status": "enabled|disabled", "updated_at": "datetime" }`

   - `DELETE /api/curves/{curve_id}` (admin only)
     - Delete a curve (logical deletion by setting status to disabled)
     - Headers: Authorization: Bearer {access_token}
     - Response: `{ "message": "Curve successfully disabled" }`

## Public Key Management

1. **User Public Keys**
   - `GET /api/public-keys`
     - List all public keys (admin only)
     - Headers: Authorization: Bearer {access_token}
     - Parameters: user_id (optional), algorithm_id (optional), curve_id (optional), status (active|revoked|expired)
     - Response: `{ "keys": [{"id": "uuid", "user_id": "uuid", "algorithm_id": "uuid", "curve_id": "uuid", "name": "string", "format": "string", "status": "string"}], "total": 100, "page": 1, "limit": 20 }`

   - `GET /api/users/{user_id}/public-keys`
     - List all public keys for a user
     - Headers: Authorization: Bearer {access_token}
     - Parameters: status (active|revoked|expired)
     - Response: `{ "keys": [{"id": "uuid", "algorithm_name": "string", "curve_name": "string", "key_data": "string", "format": "string", "name": "string", "status": "string", "created_at": "datetime"}] }`

   - `GET /api/public-keys/{key_id}`
     - Get a specific public key
     - Headers: Authorization: Bearer {access_token}
     - Response: `{ "id": "uuid", "user_id": "uuid", "algorithm_id": "uuid", "algorithm_name": "string", "curve_id": "uuid", "curve_name": "string", "key_data": "string", "format": "PEM|DER|raw", "name": "string", "metadata": {...}, "created_at": "datetime", "expires_at": "datetime", "status": "active|revoked|expired" }`

   - `POST /api/users/{user_id}/public-keys`
     - Register a new public key
     - Headers: Authorization: Bearer {access_token}
     - Request: `{ "algorithm_id": "uuid", "curve_id": "uuid", "key_data": "string", "format": "PEM|DER|raw", "name": "string", "metadata": {...}, "expires_at": "datetime" }`
     - Response: `{ "id": "uuid", "algorithm_name": "string", "curve_name": "string", "format": "string", "name": "string", "created_at": "datetime" }`

   - `PUT /api/public-keys/{key_id}`
     - Update a public key (name, metadata only)
     - Headers: Authorization: Bearer {access_token}
     - Request: `{ "name": "string", "metadata": {...}, "expires_at": "datetime" }`
     - Response: `{ "id": "uuid", "name": "string", "metadata": {...}, "expires_at": "datetime", "updated_at": "datetime" }`

   - `PATCH /api/public-keys/{key_id}/status`
     - Update public key status (revoke)
     - Headers: Authorization: Bearer {access_token}
     - Request: `{ "status": "revoked", "reason": "string" }`
     - Response: `{ "id": "uuid", "status": "revoked", "updated_at": "datetime" }`

   - `DELETE /api/public-keys/{key_id}`
     - Mark a public key as revoked (logical deletion)
     - Headers: Authorization: Bearer {access_token}
     - Response: `{ "message": "Public key successfully revoked" }`

## Signature Verification

1. **Document Verification**
   - `POST /api/verify`
     - Verify a signed document
     - Headers: Authorization: Bearer {access_token}
     - Request: `{ "document_hash": "string", "signature": "string", "public_key_id": "uuid", "algorithm_id": "uuid", "curve_id": "uuid" }`
     - Response: `{ "is_valid": true|false, "verification_id": "uuid", "verification_time": "datetime" }`

   - `GET /api/verification-records/{verification_id}`
     - Get verification details
     - Headers: Authorization: Bearer {access_token}
     - Response: `{ "id": "uuid", "user_id": "uuid", "document_hash": "string", "public_key_id": "uuid", "algorithm_id": "uuid", "algorithm_name": "string", "curve_id": "uuid", "curve_name": "string", "is_valid": true|false, "verification_time": "datetime", "metadata": {...} }`

2. **Batch Verification**
   - `POST /api/verify/batch`
     - Verify multiple signatures at once
     - Headers: Authorization: Bearer {access_token}
     - Request: `{ "items": [{"document_hash": "string", "signature": "string", "public_key_id": "uuid", "algorithm_id": "uuid", "curve_id": "uuid"}] }`
     - Response: `{ "batch_id": "uuid", "total_count": 5, "success_count": 4, "results": [{"index": 0, "is_valid": true, "verification_id": "uuid"}], "verification_time": "datetime" }`

   - `GET /api/batch-verifications/{batch_id}`
     - Get batch verification details
     - Headers: Authorization: Bearer {access_token}
     - Response: `{ "id": "uuid", "user_id": "uuid", "total_count": 5, "success_count": 4, "verification_time": "datetime", "metadata": {...} }`

   - `GET /api/batch-verifications/{batch_id}/items`
     - Get all verification records in a batch
     - Headers: Authorization: Bearer {access_token}
     - Response: `{ "batch_id": "uuid", "items": [{"index": 0, "verification_record_id": "uuid", "document_hash": "string", "is_valid": true}] }`

## Verification History

1. **User Verification History**
   - `GET /api/users/{user_id}/verification-records`
     - List verification history for a user
     - Headers: Authorization: Bearer {access_token}
     - Parameters: from_date, to_date, is_valid (true|false), page, limit
     - Response: `{ "records": [{"id": "uuid", "document_hash": "string", "algorithm_name": "string", "curve_name": "string", "is_valid": true|false, "verification_time": "datetime"}], "total": 100, "page": 1, "limit": 20 }`

   - `GET /api/users/{user_id}/batch-verifications`
     - List batch verifications for a user
     - Headers: Authorization: Bearer {access_token}
     - Parameters: from_date, to_date, page, limit
     - Response: `{ "batches": [{"id": "uuid", "total_count": 5, "success_count": 4, "verification_time": "datetime"}], "total": 100, "page": 1, "limit": 20 }`

## System Information

1. **Health Check**
   - `GET /api/health`
     - Check system health
     - Response: `{ "status": "ok", "version": "1.0.0", "timestamp": "datetime", "database": "ok", "redis": "ok" }`

2. **System Status**
   - `GET /api/system/status`
     - Get detailed system status (admin only)
     - Headers: Authorization: Bearer {access_token}
     - Response: `{ "database": {"status": "ok", "connection_pool": 5, "active_connections": 2}, "redis": {"status": "ok", "memory_usage": "10MB", "connected_clients": 3}, "algorithms": [{"name": "ECDSA", "status": "ok"}], "curves": {"total": 5, "enabled": 4, "disabled": 1} }`

## Redis-based Rate Limiting

All API endpoints are protected by Redis-based rate limiting:

1. IP-based rate limiting: Prevents abuse from a single IP address
2. User-based rate limiting: Prevents a single user from overwhelming the system
3. Endpoint-based rate limiting: Applies specific limits to sensitive endpoints

Rate limit headers included in all responses:
- `X-RateLimit-Limit`: Maximum requests allowed in the period
- `X-RateLimit-Remaining`: Remaining requests in the current period
- `X-RateLimit-Reset`: Time when the rate limit resets (Unix timestamp) 
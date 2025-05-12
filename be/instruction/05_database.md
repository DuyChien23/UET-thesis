# Database Design

## Database Technology
PostgreSQL is recommended for this system due to its robustness, transaction support, and ability to handle cryptographic data types efficiently.

## Schema Design

### Entity-Relationship Diagram

```
┌───────────────┐       ┌───────────────┐       ┌───────────────┐
│     users     │       │     roles     │       │  permissions  │
├───────────────┤       ├───────────────┤       ├───────────────┤
│ id            │       │ id            │       │ id            │
│ username      │       │ name          │       │ description   │
│ email         │       │ description   │       │ description   │
│ password_hash │       └───────┬───────┘       └──────┬────────┘
│ status        │               │                      │
└───────┬───────┘               │                      │
        │               ┌───────┴───────┐      ┌───────┴───────┐
        │               │  user_roles   │      │role_permissions│
        │               ├───────────────┤      ├───────────────┤
        │               │ user_id       │      │ role_id       │
        │               │ role_id       │      │ permission_id │
        └──────────────►└───────────────┘      └───────────────┘
        │
        │                                       ┌───────────────┐
        │                                       │  algorithms   │
        │                                       ├───────────────┤
        │                                       │ id            │
        │                                       │ name          │
        │                                       │ type          │
        │                                       │ description   │
        │                                       └───────┬───────┘
        │                                               │
        │                                               │
        │               ┌───────────────┐               │
        │               │    curves     │◄──────────────┘
        │               ├───────────────┤
        │               │ id            │
        │               │ name          │
        │               │ algorithm_id  │
        │               │ parameters    │
        │               │ description   │
        │               │ status        │
        │               └───────┬───────┘
        │                       │
        │               ┌───────┴───────┐
        └──────────────►│  public_keys  │
        │               ├───────────────┤
        │               │ id            │
        │               │ user_id       │
        │               │ algorithm_id  │
        │               │ curve_id      │
        │               │ key_data      │
        │               │ format        │
        │               │ name          │
        │               │ status        │
        │               └───────┬───────┘
        │                       │
        │                       │
        │               ┌───────┴───────────┐
        └──────────────►│ verification_records │
                        ├───────────────────┤
                        │ id                │
                        │ user_id           │
                        │ document_hash     │
                        │ public_key_id     │
                        │ algorithm_id      │
                        │ curve_id          │
                        │ is_valid          │
                        │ verification_time │
                        └─────────┬─────────┘
                                  │
            ┌───────────────┐     │
            │batch_verifications│  │
            ├───────────────┤     │
            │ id            │     │
            │ user_id       │     │
            │ total_count   │     │
            │ success_count │     │
            │ verification_time │ │
            └───────┬───────┘     │
                    │             │
            ┌───────┴───────┐     │
            │batch_verification_items│
            ├───────────────┤     │
            │ id            │     │
            │ batch_id      │     │
            │ verification_record_id │
            │ item_index    │◄────┘
            └───────────────┘
```

### Tables Schema

#### Users and Authentication

##### Table: users

| Column         | Type                      | Constraints                                                     | Description                |
|----------------|---------------------------|----------------------------------------------------------------|----------------------------|
| id             | UUID                      | PRIMARY KEY, DEFAULT gen_random_uuid()                          | Unique identifier          |
| username       | VARCHAR(64)               | NOT NULL, UNIQUE                                                | User's login name          |
| email          | VARCHAR(256)              | NOT NULL, UNIQUE                                                | User's email address       |
| password_hash  | VARCHAR(256)              | NOT NULL                                                        | Hashed password            |
| created_at     | TIMESTAMP WITH TIME ZONE  | NOT NULL, DEFAULT NOW()                                         | Account creation time      |
| updated_at     | TIMESTAMP WITH TIME ZONE  | NOT NULL, DEFAULT NOW()                                         | Last update time           |
| last_login     | TIMESTAMP WITH TIME ZONE  | NULL                                                            | Last login timestamp       |
| status         | VARCHAR(16)               | NOT NULL, DEFAULT 'active', CHECK (IN ('active', 'inactive', 'suspended')) | Account status    |

##### Table: roles

| Column         | Type                      | Constraints                                 | Description                |
|----------------|---------------------------|---------------------------------------------|----------------------------|
| id             | UUID                      | PRIMARY KEY, DEFAULT gen_random_uuid()      | Unique identifier          |
| name           | VARCHAR(32)               | NOT NULL, UNIQUE                            | Role name (e.g., 'admin')  |
| description    | TEXT                      | NULL                                        | Role description           |
| created_at     | TIMESTAMP WITH TIME ZONE  | NOT NULL, DEFAULT NOW()                     | Creation time              |

Default values:
- 'admin': System administrator with full access
- 'user': Regular user with limited access

##### Table: user_roles

| Column         | Type                      | Constraints                                 | Description                |
|----------------|---------------------------|---------------------------------------------|----------------------------|
| user_id        | UUID                      | NOT NULL, REFERENCES users(id) ON DELETE CASCADE | User reference       |
| role_id        | UUID                      | NOT NULL, REFERENCES roles(id) ON DELETE CASCADE | Role reference       |
| created_at     | TIMESTAMP WITH TIME ZONE  | NOT NULL, DEFAULT NOW()                     | Assignment time            |
|                |                           | PRIMARY KEY (user_id, role_id)              | Composite primary key      |

##### Table: permissions

| Column         | Type                      | Constraints                                 | Description                |
|----------------|---------------------------|---------------------------------------------|----------------------------|
| id             | UUID                      | PRIMARY KEY, DEFAULT gen_random_uuid()      | Unique identifier          |
| name           | VARCHAR(64)               | NOT NULL, UNIQUE                            | Permission name            |
| description    | TEXT                      | NULL                                        | Description of permission  |

Default values:
- 'manage_users': Create, update and delete users
- 'manage_curves': Add, update and delete curves
- 'verify_signatures': Verify document signatures
- 'manage_public_keys': Add and remove public keys

##### Table: role_permissions

| Column         | Type                      | Constraints                                         | Description            |
|----------------|---------------------------|-----------------------------------------------------|------------------------|
| role_id        | UUID                      | NOT NULL, REFERENCES roles(id) ON DELETE CASCADE    | Role reference         |
| permission_id  | UUID                      | NOT NULL, REFERENCES permissions(id) ON DELETE CASCADE | Permission reference |
| created_at     | TIMESTAMP WITH TIME ZONE  | NOT NULL, DEFAULT NOW()                             | Assignment time        |
|                |                           | PRIMARY KEY (role_id, permission_id)                | Composite primary key  |

#### Cryptographic Components

##### Table: algorithms

| Column         | Type                      | Constraints                                         | Description               |
|----------------|---------------------------|-----------------------------------------------------|---------------------------|
| id             | UUID                      | PRIMARY KEY, DEFAULT gen_random_uuid()              | Unique identifier         |
| name           | VARCHAR(32)               | NOT NULL, UNIQUE                                    | Algorithm name            |
| type           | VARCHAR(16)               | NOT NULL, CHECK (IN ('ECDSA', 'RSA', 'EdDSA', 'other')) | Algorithm type      |
| description    | TEXT                      | NULL                                                | Algorithm description     |
| created_at     | TIMESTAMP WITH TIME ZONE  | NOT NULL, DEFAULT NOW()                             | Creation time             |

Default values:
- 'ECDSA': Elliptic Curve Digital Signature Algorithm
- 'RSA': Rivest–Shamir–Adleman algorithm
- 'EdDSA': Edwards-curve Digital Signature Algorithm

##### Table: curves

| Column         | Type                      | Constraints                                         | Description               |
|----------------|---------------------------|-----------------------------------------------------|---------------------------|
| id             | UUID                      | PRIMARY KEY, DEFAULT gen_random_uuid()              | Unique identifier         |
| name           | VARCHAR(64)               | NOT NULL, UNIQUE                                    | Curve name                |
| algorithm_id   | UUID                      | NOT NULL, REFERENCES algorithms(id)                 | Algorithm reference       |
| parameters     | JSONB                     | NOT NULL                                            | Curve parameters          |
| description    | TEXT                      | NULL                                                | Curve description         |
| status         | VARCHAR(16)               | NOT NULL, DEFAULT 'enabled', CHECK (IN ('enabled', 'disabled')) | Curve status  |
| created_at     | TIMESTAMP WITH TIME ZONE  | NOT NULL, DEFAULT NOW()                             | Creation time             |
| updated_at     | TIMESTAMP WITH TIME ZONE  | NOT NULL, DEFAULT NOW()                             | Last update time          |

Indexes:
- idx_curves_algorithm_id ON curves(algorithm_id)

Default curves:
- 'secp256k1': Bitcoin curve
- 'P-256': NIST P-256 curve
- 'Curve25519': Curve used in Ed25519

##### Table: public_keys

| Column         | Type                      | Constraints                                         | Description               |
|----------------|---------------------------|-----------------------------------------------------|---------------------------|
| id             | UUID                      | PRIMARY KEY, DEFAULT gen_random_uuid()              | Unique identifier         |
| user_id        | UUID                      | NOT NULL, REFERENCES users(id) ON DELETE CASCADE    | User reference            |
| algorithm_id   | UUID                      | NOT NULL, REFERENCES algorithms(id)                 | Algorithm reference       |
| curve_id       | UUID                      | NULL, REFERENCES curves(id)                         | Curve reference           |
| key_data       | TEXT                      | NOT NULL                                            | Public key data           |
| format         | VARCHAR(16)               | NOT NULL, DEFAULT 'PEM', CHECK (IN ('PEM', 'DER', 'raw')) | Key format         |
| name           | VARCHAR(64)               | NULL                                                | Key name                  |
| metadata       | JSONB                     | NULL                                                | Additional metadata       |
| created_at     | TIMESTAMP WITH TIME ZONE  | NOT NULL, DEFAULT NOW()                             | Creation time             |
| expires_at     | TIMESTAMP WITH TIME ZONE  | NULL                                                | Expiration time           |
| status         | VARCHAR(16)               | NOT NULL, DEFAULT 'active', CHECK (IN ('active', 'revoked', 'expired')) | Key status |

Constraints:
- ECDSA keys must specify a curve

Indexes:
- idx_public_keys_user_id ON public_keys(user_id)
- idx_public_keys_algorithm_id ON public_keys(algorithm_id)
- idx_public_keys_curve_id ON public_keys(curve_id)

#### Verification Records

##### Table: verification_records

| Column            | Type                      | Constraints                                  | Description                |
|-------------------|---------------------------|----------------------------------------------|----------------------------|
| id                | UUID                      | PRIMARY KEY, DEFAULT gen_random_uuid()       | Unique identifier          |
| user_id           | UUID                      | NOT NULL, REFERENCES users(id)               | User reference             |
| document_hash     | VARCHAR(128)              | NOT NULL                                     | Hash of the document       |
| public_key_id     | UUID                      | NOT NULL, REFERENCES public_keys(id)         | Public key reference       |
| algorithm_id      | UUID                      | NOT NULL, REFERENCES algorithms(id)          | Algorithm reference        |
| curve_id          | UUID                      | NULL, REFERENCES curves(id)                  | Curve reference            |
| is_valid          | BOOLEAN                   | NOT NULL                                     | Verification result        |
| verification_time | TIMESTAMP WITH TIME ZONE  | NOT NULL, DEFAULT NOW()                      | Verification timestamp     |
| metadata          | JSONB                     | NULL                                         | Additional metadata        |

Constraints:
- ECDSA verifications must specify a curve

Indexes:
- idx_verification_records_user_id ON verification_records(user_id)
- idx_verification_records_public_key_id ON verification_records(public_key_id)
- idx_verification_records_verification_time ON verification_records(verification_time)

##### Table: batch_verifications

| Column            | Type                      | Constraints                                  | Description                  |
|-------------------|---------------------------|----------------------------------------------|------------------------------|
| id                | UUID                      | PRIMARY KEY, DEFAULT gen_random_uuid()       | Unique identifier            |
| user_id           | UUID                      | NOT NULL, REFERENCES users(id)               | User reference               |
| total_count       | INTEGER                   | NOT NULL                                     | Total number of verifications|
| success_count     | INTEGER                   | NOT NULL                                     | Number of successful verifs  |
| verification_time | TIMESTAMP WITH TIME ZONE  | NOT NULL, DEFAULT NOW()                      | Batch verification timestamp |
| metadata          | JSONB                     | NULL                                         | Additional metadata          |

Indexes:
- idx_batch_verifications_user_id ON batch_verifications(user_id)
- idx_batch_verifications_verification_time ON batch_verifications(verification_time)

##### Table: batch_verification_items

| Column                  | Type                      | Constraints                                           | Description                 |
|-------------------------|---------------------------|-------------------------------------------------|------------------------------|
| id                      | UUID                      | PRIMARY KEY, DEFAULT gen_random_uuid()         | Unique identifier            |
| batch_id                | UUID                      | NOT NULL, REFERENCES batch_verifications(id) ON DELETE CASCADE | Batch reference   |
| verification_record_id  | UUID                      | NOT NULL, REFERENCES verification_records(id)  | Verification record reference|
| item_index              | INTEGER                   | NOT NULL                                       | Item position in batch       |
|                         |                           | UNIQUE(batch_id, item_index)                   | Ensures unique index per batch|

Indexes:
- idx_batch_verification_items_batch_id ON batch_verification_items(batch_id)

## Database Migrations

The system should include database migration scripts to manage schema changes and updates. Consider using tools like Alembic (for Python) to handle migrations.

## Data Access Layer

Implement a data access layer that abstracts database operations from the business logic. This layer should:

1. Use parameterized queries to prevent SQL injection
2. Implement transaction management for operations that affect multiple tables
3. Include retry logic for handling transient database errors
4. Support connection pooling for performance
5. Provide clear error handling and logging

## Indexing Strategy

The database design includes indexes on frequently queried columns to optimize performance:

1. Foreign keys for relationship lookups
2. Timestamp fields for date range queries
3. Status fields for filtering active/inactive records
4. Unique constraints on fields requiring uniqueness

## Security Considerations

1. Store all sensitive data (passwords, tokens) as hashed values
2. Use encrypted connections to the database
3. Implement row-level security where appropriate
4. Use least-privilege database users for application connections
5. Regularly audit database access and operations 

## Redis Caching Layer

In addition to the PostgreSQL database, the system will utilize Redis as a high-performance caching layer to optimize performance and scalability.

### Redis Configuration

The Redis instance should be configured with:

1. Persistence enabled (AOF mode with fsync every second)
2. Appropriate memory limits based on expected workload
3. Password authentication and TLS encryption
4. Redis Sentinel or Redis Cluster for high availability (production)

### Key Redis Use Cases

#### JWT Token Management

| Key Pattern | Value Type | TTL | Purpose |
|-------------|------------|-----|---------|
| `blacklist:token:{token_id}` | String | Token expiration time | Store revoked/invalid tokens |
| `jwtkeys:{key_id}` | String | Long (rotated) | Cache public keys used for JWT verification |

#### API Rate Limiting

| Key Pattern | Value Type | TTL | Purpose |
|-------------|------------|-----|---------|
| `ratelimit:ip:{ip_address}` | Counter | Short (1-5 min) | Track requests per IP |
| `ratelimit:user:{user_id}` | Counter | Short (1-5 min) | Track requests per user |
| `ratelimit:endpoint:{endpoint}` | Counter | Short (1-5 min) | Track requests per endpoint |

#### Data Caching

| Key Pattern | Value Type | TTL | Purpose |
|-------------|------------|-----|---------|
| `cache:algorithms` | Hash | Medium (1 hour) | Cache algorithm information |
| `cache:curves` | Hash | Medium (1 hour) | Cache curve information |
| `cache:public_key:{key_id}` | String | Medium (1 hour) | Cache frequently used public keys |
| `cache:user:{user_id}` | Hash | Short (15 min) | Cache user data excluding sensitive info |

#### Verification Results Cache

| Key Pattern | Value Type | TTL | Purpose |
|-------------|------------|-----|---------|
| `verify:doc:{document_hash}:key:{public_key_id}` | Boolean | Medium (1-24 hours) | Cache verification results |
| `verify:recent:{user_id}` | List | Short (30 min) | Cache recent verification history |

### Cache Invalidation Strategy

1. **Time-based expiration**: Primary invalidation method using appropriate TTLs
2. **Event-based invalidation**: Publish cache invalidation events when data changes
3. **Pattern-based deletion**: For bulk invalidation (e.g., all keys for a user)

### Redis Pub/Sub Channels

| Channel | Purpose |
|---------|---------|
| `cache:invalidate` | Broadcast cache invalidation events |
| `system:events` | System-wide notifications |
| `audit:events` | Security audit events |

### Implementation Considerations

1. **Connection Pooling**: Use connection pooling for efficient Redis client management
2. **Error Handling**: Implement graceful fallback to database when Redis is unavailable
3. **Monitoring**: Set up monitoring for Redis memory usage, hit/miss ratio, and latency
4. **Data Serialization**: Use efficient serialization (MessagePack, Protocol Buffers)
5. **Atomic Operations**: Leverage Redis atomic operations for counters and locks

### Redis Commands for Common Operations

```
# Check if a token is blacklisted
EXISTS blacklist:token:{token_id}

# Add token to blacklist with TTL
SETEX blacklist:token:{token_id} {ttl_seconds} 1

# Rate limiting with sliding window
INCR ratelimit:user:{user_id}
EXPIRE ratelimit:user:{user_id} 60

# Cache public key
SETEX cache:public_key:{key_id} 3600 "{public_key_data}"

# Cache verification result
SETEX verify:doc:{document_hash}:key:{public_key_id} 86400 "{is_valid}"

# Track recent verifications (limited to 20)
LPUSH verify:recent:{user_id} "{verification_data}"
LTRIM verify:recent:{user_id} 0 19
```

### Redis Integration with Database

The Redis caching layer should be tightly integrated with the PostgreSQL database:

1. Implement a cache-aside pattern for most data access patterns
2. Use write-through caching for frequently accessed data
3. Consider using Redis Streams for event logging and processing
4. Implement a circuit breaker pattern for database fallback
5. Use consistent hashing for distributed cache scenarios

This Redis implementation will significantly improve system performance, reduce database load, and enhance scalability while maintaining data consistency. 

## Docker
Add docker for postgres and redis 
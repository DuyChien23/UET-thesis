# Digital Signature System Backend

A modular digital signature system backend that supports multiple signature algorithms with a focus on security and extensibility.

## Features

- Support for multiple signature algorithms (ECDSA, RSA, EdDSA)
- Management of elliptic curves (secp256k1, P-256, Curve25519)
- Server-side signature verification
- Public key storage and management
- Role-based access control
- Comprehensive REST API
- Redis caching for performance optimization

## Architecture

The system follows a modular architecture inspired by Java Cryptography Architecture (JCA), with these main components:

- Algorithm Provider Interface
- Algorithm Registry
- Public Key Management
- Verification Service
- User Interface Layer (REST API)

## Technologies

- Python 3.8+
- FastAPI for REST API
- PostgreSQL for data storage
- Redis for caching and token management
- SQLAlchemy ORM
- Docker and Docker Compose for containerization

## Security

- Private keys remain with clients, never sent to the server
- JWT-based authentication with token blacklisting
- Role-based access control
- Rate limiting
- Input validation
- Secure database access

## Setup and Installation

### Prerequisites

- Docker and Docker Compose
- Python 3.8+

### Development Setup

1. Clone the repository:
   ```
   git clone https://github.com/your-organization/digital-signature-system.git
   cd digital-signature-system/be
   ```

2. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Copy the example environment file:
   ```
   cp .env.example .env
   ```

5. Start services with Docker Compose:
   ```
   docker-compose up -d
   ```

6. Run migrations:
   ```
   sh scripts/run_migrations.sh
   ```

7. Start the development server:
   ```
   uvicorn src.api.app:app --reload
   ```

8. Access the API documentation at http://localhost:8000/docs

### Database Management

The application supports automatic table generation from SQLAlchemy models.

#### Using the CLI Tool

The backend includes a CLI tool for database management:

```bash
# Generate all tables from models
python -m src.cli create-tables

# Drop and re-create all tables
python -m src.cli create-tables --drop-first

# Create specific tables
python -m src.cli create-tables --tables users roles permissions
```

#### Automatic Table Creation

By default, tables are automatically created at application startup. This behavior can be controlled with the `AUTO_CREATE_TABLES` environment variable:

```
AUTO_CREATE_TABLES=true  # Enable automatic table creation (default)
AUTO_CREATE_TABLES=false # Disable automatic table creation
```

### Running Tests

```
pytest
```

### Production Deployment

For production deployment, consider:
- Using a dedicated PostgreSQL server
- Setting up Redis Sentinel/Cluster for high availability
- Using a reverse proxy (Nginx) in front of the application
- Setting appropriate environment variables for production

## API Documentation

Once the application is running, detailed API documentation can be accessed at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## License

MIT 
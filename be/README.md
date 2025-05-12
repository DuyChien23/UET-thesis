# UET-thesis

### Topic: Our system uses ECDSA (Elliptic Curve Digital Signature Algorithm) to ensure secure and verifiable digital signatures

## Project Overview
This project implements a secure digital signature service using ECDSA (Elliptic Curve Digital Signature Algorithm). It allows users to sign any type of data (text, files) and verify signatures with high security standards.

## Features
- User registration and authentication with JWT
- Key pair generation with various ECDSA curves (secp256k1, secp384r1, secp521r1)
- Secure encryption of private keys
- Text and file signing
- Signature verification
- Full API documentation with Swagger UI

## Technical Requirements
- Python 3.9+
- FastAPI
- PostgreSQL
- Docker and Docker Compose

## Installation and Setup

### 1. Clone the repository
```bash
git clone https://github.com/yourusername/UET-thesis.git
cd UET-thesis
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Database setup
Start the PostgreSQL database using Docker:
```bash
docker-compose up -d
```

### 4. Run migrations
```bash
python -m alembic upgrade head
```

### 5. Start the application
```bash
python -m uvicorn main:app --reload
```

The API will be available at http://localhost:8000

## API Documentation
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API Endpoints

### Authentication
- POST `/users/register` - Register a new user
- POST `/users/login` - Log in and get JWT token

### Key Pair Management
- POST `/key-pairs/` - Create a new ECDSA key pair
- GET `/key-pairs/` - Get all user key pairs
- GET `/key-pairs/{key_pair_id}` - Get a specific key pair

### Signatures
- POST `/signatures/sign/text` - Sign text data
- POST `/signatures/sign/file` - Sign a file
- POST `/signatures/verify` - Verify a signature
- GET `/signatures/user` - Get all user signatures
- GET `/signatures/{signature_id}` - Get a specific signature

## Security Features
- Password hashing with bcrypt
- JWT authentication
- Private key encryption
- Strong ECDSA curves (up to secp521r1)

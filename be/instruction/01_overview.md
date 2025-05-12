# Digital Signature System Backend Generator

## Project Overview

This project aims to create a modular digital signature system that supports multiple signature algorithms, with a primary focus on ECDSA (Elliptic Curve Digital Signature Algorithm) using different curves including Curve25519.

## System Architecture

The system follows a modular architecture inspired by Java Cryptography Architecture (JCA), with the following main components:

1. **Algorithm Provider Interface**: Defines standard interfaces for signature verification algorithms
2. **Algorithm Registry**: Manages and provides access to different algorithm implementations
3. **Public Key Management**: Handles public key storage and retrieval
4. **Verification Service**: Handles signature verification operations
5. **User Interface Layer**: Provides CLI and REST API interfaces 
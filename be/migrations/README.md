# Database Migrations

This directory contains database migration scripts for the UET Thesis project.

## Migration Files

- `001_seed_algorithms_and_admin.py`: Seeds the database with algorithms, curves, roles, and a default admin user
- `002_seed_default_data.py`: Seeds the database with sample data for testing (public keys, verification records, batch verifications, and a test user)

## Running Migrations

You can run the migrations using the CLI tool:

```bash
# Run all migrations
python -m src.cli seed-data
```

Or by using the `postgres_migrate.sh` script which will:
1. Create all database tables
2. Run all migration scripts

```bash
./postgres_migrate.sh
```

## Default User Accounts

The migrations create the following default user accounts:

1. Admin user:
   - Username: `admin`
   - Email: `admin@example.com`
   - Password: `admin123`
   - Role: admin

2. Test user:
   - Username: `testuser`
   - Email: `test@example.com`
   - Password: `test123`
   - Role: user

## Creating New Migrations

When creating a new migration script:

1. Use a sequential numbering format (e.g., `003_migration_name.py`)
2. Implement the `run_migration()` function that performs the migration
3. Implement the `check_if_migration_needed()` function to avoid duplicate runs 
4. Include a `main()` function to allow standalone execution
5. Update the README to document the new migration 
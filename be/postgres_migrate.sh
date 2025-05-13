#!/bin/bash

# Thiết lập biến môi trường cho PostgreSQL
export MOCK_SERVICES=false
export AUTO_CREATE_TABLES=true
export DATABASE_URL=postgresql+asyncpg://signature_user:signature_password@localhost:5432/signature_db
export POSTGRES_USER=signature_user
export POSTGRES_PASSWORD=signature_password
export POSTGRES_DB=signature_db
export POSTGRES_PORT=5432
export POSTGRES_HOST=localhost

# Kích hoạt môi trường ảo nếu có
if [ -d "venv" ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
fi

# Đường dẫn python
PYTHON_CMD=$(which python3 || which python)

if [ -z "$PYTHON_CMD" ]; then
    echo "Python not found! Please make sure Python is installed."
    exit 1
fi

echo "Generating tables to PostgreSQL database..."

# Sử dụng CLI tool để tạo các bảng
echo "Using CLI tool to create tables..."
$PYTHON_CMD -m src.cli create-tables

echo "Database tables created successfully!"
echo "You can now run the application with PostgreSQL using:"
echo "./postgres_run.sh" 
#!/bin/bash

# Đảm bảo biến môi trường AUTO_CREATE_TABLES được thiết lập thành true
export AUTO_CREATE_TABLES=true

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

echo "Starting development server with auto-reload and database auto-creation..."
echo "Using Python at: $PYTHON_CMD"

# Chạy uvicorn với các tùy chọn
$PYTHON_CMD -m uvicorn src.main:app --reload --host 0.0.0.0 --port 8000 
"""
FastAPI application entry point.
"""

import sys
import os

# Add the parent directory to the path so relative imports work
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from src.main import app 
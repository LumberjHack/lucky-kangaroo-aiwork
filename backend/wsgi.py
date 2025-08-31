"""
WSGI config for Lucky Kangaroo backend.

This module contains the WSGI application used by the production server.
"""

import os
import sys
from pathlib import Path

# Add the project directory to the Python path
project_root = Path(__file__).parent.absolute()
sys.path.insert(0, str(project_root))

# Set the environment variables
os.environ.setdefault('FLASK_APP', 'app:create_app()')
os.environ.setdefault('FLASK_ENV', 'production')

# Import the application
from app import create_app  # noqa: E402 - import after env setup is intentional

# Create the application instance
application = create_app()

if __name__ == "__main__":
    # This is used when running the application directly (e.g., for development)
    application.run(host='0.0.0.0', port=5000)

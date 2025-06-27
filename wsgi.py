import sys
import os

# Add the project directory to Python path
sys.path.insert(0, os.path.dirname(__file__))

# Import from the venv directory where your __init__.py is located
from venv import create_app

# Create the Flask application instance
application = create_app()

if __name__ == "__main__":
    application.run()

import sys
import os

# Add the project directory to Python path
sys.path.insert(0, os.path.dirname(__file__))

# Import from the app directory
from app import create_app

# Create the Flask application instance
application = create_app()

if __name__ == "__main__":
    # Railway provides PORT environment variable
    port = int(os.environ.get('PORT', 8080))
    application.run(host='0.0.0.0', port=port, debug=False)
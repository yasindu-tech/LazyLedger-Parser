#!/usr/bin/env python3
"""
Local development server for LazyLedger-Parser
Run this script to start the Flask development server
"""

import os
from app import create_app

if __name__ == '__main__':
    # Create the Flask app
    app = create_app()
    
    # Run in debug mode for development
    app.run(
        host='127.0.0.1',  # localhost only for security
        port=5000,         # default Flask port
        debug=True,        # auto-reload on code changes
        use_reloader=True  # restart on file changes
    )

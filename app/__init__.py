from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import os

from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file
db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    
    # Enable CORS for all domains and routes
    CORS(app, origins=[
        "https://lazy-ledger-frontend.vercel.app",
        "http://localhost:3000",  # For local development
        "http://127.0.0.1:3000"   # Alternative local address
    ])
    
    # Configure the database URI from environment variables
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize the database with the Flask app
    db.init_app(app)

    # Import and register the extraction blueprint
    from .api.parser import parser as parser_blueprint
    app.register_blueprint(parser_blueprint)
    
    # Import and register the transactions blueprint
    from .api.transactions import transactions_bp
    app.register_blueprint(transactions_bp)
    
    # Import and register the insights blueprint
    from .api.insights_routes import insights_bp
    app.register_blueprint(insights_bp)
    
    # Add a simple health check endpoint
    @app.route('/health')
    def health_check():
        return {'status': 'healthy', 'message': 'LazyLedger API is running'}

    return app

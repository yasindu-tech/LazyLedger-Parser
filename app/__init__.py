from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import os

from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file
db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    
    # Enable CORS for known origins and ensure preflight responses include headers
    CORS(app,
         resources={r"/*": {"origins": [
             "https://lazy-ledger-frontend.vercel.app",
             "http://localhost:3000",
             "http://127.0.0.1:3000"
         ]}},
         supports_credentials=True,
         allow_headers=["Content-Type", "Authorization", "X-Requested-With", "X-Request-Id"],
         methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    )

    # Defensive fallback: ensure all responses include necessary CORS headers
    @app.after_request
    def add_cors_headers(response):
        origin = request.headers.get('Origin')
        allowed = [
            "https://lazy-ledger-frontend.vercel.app",
            "http://localhost:3000",
            "http://127.0.0.1:3000"
        ]
        if origin and origin in allowed:
            response.headers['Access-Control-Allow-Origin'] = origin
            # Ensure caches vary by Origin
            response.headers['Vary'] = 'Origin'
        # Always expose these for clients that need them
        response.headers['Access-Control-Allow-Credentials'] = 'true'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Requested-With, X-Request-Id'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
        return response
    
    # Configure the database URI from environment variables
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize the database with the Flask app
    db.init_app(app)

    # Import and register the extraction blueprint
    from .api.parser import parser as parser_blueprint
    app.register_blueprint(parser_blueprint)
    # Import and register raw-records blueprint (create endpoint that inserts raw entries and transactions)
    from .api.raw_records import raw_bp as raw_records_bp
    app.register_blueprint(raw_records_bp)
    
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

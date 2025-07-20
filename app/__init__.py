from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os

from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file
db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    
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

    return app

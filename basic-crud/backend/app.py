from flask import Flask
from flask_cors import CORS
import os
from dotenv import load_dotenv

from extensions import db, bcrypt

load_dotenv()

app = Flask(__name__)

# CORS only for API routes; tighten origins later for prod
CORS(app, resources={r"/api/*": {"origins": "*"}})

# ---- Config ----
app.config['ENV'] = os.getenv('FLASK_ENV')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
# Optional but helpful to avoid stale DB connections
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {"pool_pre_ping": True}

# Fail fast if critical envs missing
if not app.config['SQLALCHEMY_DATABASE_URI'] or not app.config['SECRET_KEY']:
    raise RuntimeError("DATABASE_URL and SECRET_KEY must be set in .env")

# ---- Init extensions ----
db.init_app(app)
bcrypt.init_app(app)

# Import models AFTER init so SQLAlchemy registers them
from models import User
from routes import api_bp

# Mount blueprint under /api (matches your CORS scope)
app.register_blueprint(api_bp, url_prefix='/api')

# Create tables for a fresh dev setup
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=(app.config['ENV'] == 'development'))

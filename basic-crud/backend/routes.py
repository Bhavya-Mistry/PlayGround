from flask import Blueprint, request, jsonify
from app import db, bcrypt
from models import User, AIModel
import uuid

api_bp = Blueprint('api', __name__)

# User Registration
@api_bp.route('/register', methods=['POST'])
def register():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    if not email or not password:
        return jsonify({'error': 'Email and password required'}), 400
    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'Email already exists'}), 409
    hashed_pw = bcrypt.generate_password_hash(password).decode('utf-8')
    api_key = str(uuid.uuid4())
    user = User(email=email, password=hashed_pw, api_key=api_key)
    db.session.add(user)
    db.session.commit()
    return jsonify({'message': 'User registered successfully', 'api_key': api_key}), 201

# User Login
@api_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    user = User.query.filter_by(email=email).first()
    if user and bcrypt.check_password_hash(user.password, password):
        return jsonify({'message': 'Login successful', 'api_key': user.api_key}), 200
    return jsonify({'error': 'Invalid credentials'}), 401

# CRUD for User
@api_bp.route('/users', methods=['POST'])
def create_user():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    credits = data.get('credits', 0)
    api_key = str(uuid.uuid4())
    hashed_pw = bcrypt.generate_password_hash(password).decode('utf-8')
    user = User(email=email, password=hashed_pw, credits=credits, api_key=api_key)
    db.session.add(user)
    db.session.commit()
    return jsonify({'id': user.id, 'email': user.email, 'credits': user.credits, 'api_key': user.api_key}), 201

@api_bp.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    return jsonify([{'id': u.id, 'email': u.email, 'credits': u.credits, 'api_key': u.api_key} for u in users])

@api_bp.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = User.query.get_or_404(user_id)
    return jsonify({'id': user.id, 'email': user.email, 'credits': user.credits, 'api_key': user.api_key})

@api_bp.route('/users/<int:user_id>', methods=['PATCH'])
def update_user(user_id):
    user = User.query.get_or_404(user_id)
    data = request.json
    if 'email' in data:
        user.email = data['email']
    if 'password' in data:
        user.password = bcrypt.generate_password_hash(data['password']).decode('utf-8')
    if 'credits' in data:
        user.credits = data['credits']
    db.session.commit()
    return jsonify({'message': 'User updated'})

@api_bp.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    return jsonify({'message': 'User deleted'})

# CRUD for AI Models
@api_bp.route('/models', methods=['POST'])
def create_model():
    data = request.json
    name = data.get('name')
    version = data.get('version')
    model = AIModel(name=name, version=version)
    db.session.add(model)
    db.session.commit()
    return jsonify({'id': model.id, 'name': model.name, 'version': model.version}), 201

@api_bp.route('/models', methods=['GET'])
def get_models():
    models = AIModel.query.all()
    return jsonify([{'id': m.id, 'name': m.name, 'version': m.version} for m in models])

@api_bp.route('/models/<int:model_id>', methods=['GET'])
def get_model(model_id):
    model = AIModel.query.get_or_404(model_id)
    return jsonify({'id': model.id, 'name': model.name, 'version': model.version})

@api_bp.route('/models/<int:model_id>', methods=['PATCH'])
def update_model(model_id):
    model = AIModel.query.get_or_404(model_id)
    data = request.json
    if 'name' in data:
        model.name = data['name']
    if 'version' in data:
        model.version = data['version']
    db.session.commit()
    return jsonify({'message': 'Model updated'})

@api_bp.route('/models/<int:model_id>', methods=['DELETE'])
def delete_model(model_id):
    model = AIModel.query.get_or_404(model_id)
    db.session.delete(model)
    db.session.commit()
    return jsonify({'message': 'Model deleted'})

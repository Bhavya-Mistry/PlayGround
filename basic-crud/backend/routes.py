# from flask import Blueprint, request, jsonify
# from app import db, bcrypt
# from models import User, AIModel
# import uuid


# # lets you group routes separately from the main app and register them later in app.py.
# api_bp = Blueprint('api', __name__)

# # User Registration
# @api_bp.route('/register', methods=['POST'])
# def register():

#     # Flow: HTTP POST → validate → hash password → insert → commit → JSON response.

#     data = request.json
#     email = data.get('email')
#     password = data.get('password')
    
    
#     # Validates they exist; else 400 Bad Request.
#     if not email or not password:
#         return jsonify({'error': 'Email and password required'}), 400
    
    
#     # Checks email uniqueness;
#     # SELECT * FROM usertable WHERE email = 'given_email';
#     # This is a simple check to ensure the email is not already registered.
#     # If true, meaning the email already exists, it returns a 409 Conflict.
#     if User.query.filter_by(email=email).first():
#         return jsonify({'error': 'Email already exists'}), 409
     
#     # Hashes password using bcrypt (so we never store plain text).
#     hashed_pw = bcrypt.generate_password_hash(password).decode('utf-8')
    
#     # Generates a unique API key for the user.
#     api_key = str(uuid.uuid4())

#     user = User(email=email, password=hashed_pw, api_key=api_key)
#     db.session.add(user)
#     db.session.commit()

#     return jsonify({'message': 'User registered successfully', 'api_key': api_key}), 201

# # User Login
# @api_bp.route('/login', methods=['POST'])
# def login():
#     data = request.json
#     email = data.get('email')
#     password = data.get('password')

#     if not email or not password:
#         return jsonify({'error': 'Email and password required'}), 400

#     user = User.query.filter_by(email=email).first()

#     if not user:
#         return jsonify({'error': 'User not found'}), 401
    
#     if not bcrypt.check_password_hash(user.password, password):
#         return jsonify({'error': 'Invalid credentials'}), 401

#     return jsonify({'message': 'Login Successful','api_key': user.api_key}), 200


# # ADMIN STUFF
# # This is a placeholder for admin routes.
# # You can add routes here to manage users, AI models, etc.
# import os
# from functools import wraps
    
# ADMIN_EMAIL = os.getenv('ADMIN_EMAIL', '').strip().lower()
# ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', '')
# ADMIN_API_KEY = os.getenv('ADMIN_API_KEY', '')


# # # CRUD for User
# # @api_bp.route('/users', methods=['POST'])
# # def create_user():
# #     data = request.json
# #     email = data.get('email')
# #     password = data.get('password')
# #     credits = data.get('credits', 0)
# #     api_key = str(uuid.uuid4())
# #     hashed_pw = bcrypt.generate_password_hash(password).decode('utf-8')
# #     user = User(email=email, password=hashed_pw, credits=credits, api_key=api_key)
# #     db.session.add(user)
# #     db.session.commit()
# #     return jsonify({'id': user.id, 'email': user.email, 'credits': user.credits, 'api_key': user.api_key}), 201

# # @api_bp.route('/users', methods=['GET'])
# # def get_users():
# #     users = User.query.all()
# #     return jsonify([{'id': u.id, 'email': u.email, 'credits': u.credits, 'api_key': u.api_key} for u in users])

# # @api_bp.route('/users/<int:user_id>', methods=['GET'])
# # def get_user(user_id):
# #     user = User.query.get_or_404(user_id)
# #     return jsonify({'id': user.id, 'email': user.email, 'credits': user.credits, 'api_key': user.api_key})

# # @api_bp.route('/users/<int:user_id>', methods=['PATCH'])
# # def update_user(user_id):
# #     user = User.query.get_or_404(user_id)
# #     data = request.json
# #     if 'email' in data:
# #         user.email = data['email']
# #     if 'password' in data:
# #         user.password = bcrypt.generate_password_hash(data['password']).decode('utf-8')
# #     if 'credits' in data:
# #         user.credits = data['credits']
# #     db.session.commit()
# #     return jsonify({'message': 'User updated'})

# # @api_bp.route('/users/<int:user_id>', methods=['DELETE'])
# # def delete_user(user_id):
# #     user = User.query.get_or_404(user_id)
# #     db.session.delete(user)
# #     db.session.commit()
# #     return jsonify({'message': 'User deleted'})

# # # CRUD for AI Models
# # @api_bp.route('/models', methods=['POST'])
# # def create_model():
# #     data = request.json
# #     name = data.get('name')
# #     version = data.get('version')
# #     model = AIModel(name=name, version=version)
# #     db.session.add(model)
# #     db.session.commit()
# #     return jsonify({'id': model.id, 'name': model.name, 'version': model.version}), 201

# # @api_bp.route('/models', methods=['GET'])
# # def get_models():
# #     models = AIModel.query.all()
# #     return jsonify([{'id': m.id, 'name': m.name, 'version': m.version} for m in models])

# # @api_bp.route('/models/<int:model_id>', methods=['GET'])
# # def get_model(model_id):
# #     model = AIModel.query.get_or_404(model_id)
# #     return jsonify({'id': model.id, 'name': model.name, 'version': model.version})

# # @api_bp.route('/models/<int:model_id>', methods=['PATCH'])
# # def update_model(model_id):
# #     model = AIModel.query.get_or_404(model_id)
# #     data = request.json
# #     if 'name' in data:
# #         model.name = data['name']
# #     if 'version' in data:
# #         model.version = data['version']
# #     db.session.commit()
# #     return jsonify({'message': 'Model updated'})

# # @api_bp.route('/models/<int:model_id>', methods=['DELETE'])
# # def delete_model(model_id):
# #     model = AIModel.query.get_or_404(model_id)
# #     db.session.delete(model)
# #     db.session.commit()
# #     return jsonify({'message': 'Model deleted'})


'''------------------------------------------------------------------------------------------------'''

from flask import Blueprint, request, jsonify, g
from functools import wraps
import uuid

from extensions import db, bcrypt
from models import User

api_bp = Blueprint('api', __name__)

# ---------- Auth helpers ----------

def auth_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        if not api_key:
            return jsonify({'error': 'Missing X-API-Key header'}), 401
        user = User.query.filter_by(api_key=api_key).first()
        if not user:
            return jsonify({'error': 'Invalid or expired API key'}), 401
        g.current_user = user
        return f(*args, **kwargs)
    return wrapper

def admin_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        if not api_key:
            return jsonify({'error': 'Missing X-API-Key header'}), 401
        user = User.query.filter_by(api_key=api_key).first()
        if not user or not user.is_admin:
            return jsonify({'error': 'Admin access required'}), 403
        g.current_user = user
        return f(*args, **kwargs)
    return wrapper

# ---------- Auth: signup / signin ----------

@api_bp.route('/signup', methods=['POST'])
def signup():
    data = request.get_json(silent=True) or {}
    email = (data.get('email') or '').strip().lower()
    password = data.get('password') or ''

    if not email or not password:
        return jsonify({'error': 'Email and password required'}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'Email already exists'}), 409

    hashed_pw = bcrypt.generate_password_hash(password).decode('utf-8')
    api_key = str(uuid.uuid4())

    user = User(email=email, password=hashed_pw, api_key=api_key, credits=0, is_admin=False)
    db.session.add(user)
    db.session.commit()

    return jsonify({'message': 'Signup successful', 'api_key': api_key}), 201


@api_bp.route('/signin', methods=['POST'])
def signin():
    data = request.get_json(silent=True) or {}
    email = (data.get('email') or '').strip().lower()
    password = data.get('password') or ''

    if not email or not password:
        return jsonify({'error': 'Email and password required'}), 400

    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({'error': 'Invalid credentials'}), 401

    if not bcrypt.check_password_hash(user.password, password):
        return jsonify({'error': 'Invalid credentials'}), 401

    return jsonify({'message': 'Signin successful', 'api_key': user.api_key}), 200

# ---------- User dashboard (self) ----------

@api_bp.route('/me', methods=['GET'])
@auth_required
def me():
    u = g.current_user
    return jsonify({
        'id': u.id,
        'email': u.email,
        'credits': u.credits,
        'is_admin': u.is_admin,
        'created_at': u.created_at.isoformat() if u.created_at else None,
        'updated_at': u.updated_at.isoformat() if u.updated_at else None
    }), 200

# ---------- Admin: CRUD on users ----------

@api_bp.route('/admin/users', methods=['POST'])
@admin_required
def admin_create_user():
    data = request.get_json(silent=True) or {}
    email = (data.get('email') or '').strip().lower()
    password = data.get('password') or ''
    credits = int(data.get('credits', 0))
    is_admin = bool(data.get('is_admin', False))

    if not email or not password:
        return jsonify({'error': 'Email and password required'}), 400
    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'Email already exists'}), 409

    hashed_pw = bcrypt.generate_password_hash(password).decode('utf-8')
    api_key = str(uuid.uuid4())

    user = User(email=email, password=hashed_pw, api_key=api_key,
                credits=credits, is_admin=is_admin)
    db.session.add(user)
    db.session.commit()

    return jsonify({
        'id': user.id, 'email': user.email, 'credits': user.credits,
        'is_admin': user.is_admin, 'api_key': user.api_key
    }), 201


@api_bp.route('/admin/users', methods=['GET'])
@admin_required
def admin_list_users():
    q = User.query.order_by(User.id.asc()).all()
    return jsonify([
        {'id': u.id, 'email': u.email, 'credits': u.credits, 'is_admin': u.is_admin}
        for u in q
    ]), 200


@api_bp.route('/admin/users/<int:user_id>', methods=['GET'])
@admin_required
def admin_get_user(user_id):
    u = User.query.get_or_404(user_id)
    return jsonify({'id': u.id, 'email': u.email, 'credits': u.credits, 'is_admin': u.is_admin}), 200


@api_bp.route('/admin/users/<int:user_id>', methods=['PATCH'])
@admin_required
def admin_update_user(user_id):
    u = User.query.get_or_404(user_id)
    data = request.get_json(silent=True) or {}

    if 'email' in data:
        new_email = (data['email'] or '').strip().lower()
        if not new_email:
            return jsonify({'error': 'Email cannot be empty'}), 400
        if new_email != u.email and User.query.filter_by(email=new_email).first():
            return jsonify({'error': 'Email already exists'}), 409
        u.email = new_email

    if 'password' in data and data['password']:
        u.password = bcrypt.generate_password_hash(data['password']).decode('utf-8')

    if 'credits' in data:
        try:
            u.credits = int(data['credits'])
        except ValueError:
            return jsonify({'error': 'credits must be an integer'}), 400

    if 'is_admin' in data:
        u.is_admin = bool(data['is_admin'])

    db.session.commit()
    return jsonify({'message': 'User updated'}), 200


@api_bp.route('/admin/users/<int:user_id>', methods=['DELETE'])
@admin_required
def admin_delete_user(user_id):
    u = User.query.get_or_404(user_id)
    db.session.delete(u)
    db.session.commit()
    return jsonify({'message': 'User deleted'}), 200

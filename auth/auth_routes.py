from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt, create_access_token
from student.models import Student
from datetime import timedelta

# Create a blueprint for auth
auth_bp = Blueprint('auth', __name__, url_prefix='/api')

revoked_tokens = set()

@auth_bp.route('/v1/login', methods=['POST'])
def login():
    data = request.get_json()

    # Validate input data
    if not data or 'username' not in data or 'password' not in data:
        return jsonify({"message": "Username and password are required"}), 400

    # Check if the user exists
    student = Student.query.filter_by(username=data['username']).first()
    if not student or not student.check_password(data['password']):
        return jsonify({"message": "Invalid username or password"}), 401

    # Create a JWT token with an expiration time
    access_token = create_access_token(identity=student.id, expires_delta=timedelta(minutes=30))
    return jsonify(access_token=access_token), 200

@auth_bp.route('/v1/logout', methods=['POST'])
@jwt_required()
def logout():
    # Get the unique identifier for the token (jti) and add it to the blacklist
    jti = get_jwt()['jti']
    revoked_tokens.add(jti)
    return jsonify({"message": "Successfully logged out"}), 200

# A blocklisted access token will not be able to access this any more
@auth_bp.route("/protected", methods=["GET"])
@jwt_required()
def protected():
    return jsonify(hello="world")
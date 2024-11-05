from flask import Blueprint, jsonify, request
from .schemas import student_schema
from marshmallow import ValidationError
from .models import Student, db

# Initialize the Blueprint here in routes.py
student_bp = Blueprint('student', __name__, url_prefix='/api/student')


@student_bp.route('/v1/register', methods=['POST'])
def register():
    # Load and validate input data using the schema
    try:
        data = student_schema.load(request.get_json())
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400

    # Check if the username or email already exists
    if Student.query.filter_by(username=data['username']).first():
        return jsonify({"message": "Username already taken"}), 409
    if Student.query.filter_by(email=data['email']).first():
        return jsonify({"message": "Email already registered"}), 409

    # Create and save the new student
    new_student = Student(
        name=data['name'],
        email=data['email'],
        username=data['username']
    )
    new_student.set_password(data['password'])
    db.session.add(new_student)
    db.session.commit()

    # Serialize the output and return the created student data
    return jsonify(student_schema.dump(new_student)), 201
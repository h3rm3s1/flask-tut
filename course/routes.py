from flask import jsonify, request
from .models import Course, db
from student.models import Student
from flask import Blueprint
from marshmallow import ValidationError
from .schemas import CourseInputSchema
from flask_graphql import GraphQLView
from .schemas import schema
from flask import g

course_bp = Blueprint('course', __name__, url_prefix='/api')

@course_bp.route('/v1/create', methods=['POST'])
def create_course():
    data = request.get_json()

    user_ip = g.user_ip

    # Validate input data
    schema = CourseInputSchema()
    try:
        validated_data = schema.load(data)
    except ValidationError as err:
        return jsonify(err.messages), 400

    # Ensure student exists
    student = Student.query.get(validated_data['student_id'])
    if not student:
        return jsonify({"message": "Student not found"}), 404

    # Create and save the new course
    course = Course(
        name=validated_data['name'],
        description=validated_data.get('description'),
        student_id=validated_data['student_id']
    )
    db.session.add(course)
    db.session.commit()

    return jsonify({"message": "course created successfully", "course": {
        "id": course.id,
        "name": course.name,
        "description": course.description,
        "student_id": course.student_id,
        "user_ip": user_ip,
    }}), 201

course_bp.add_url_rule(
    '/v1/courses/graphql',  # Set the endpoint for GraphQL queries
    view_func=GraphQLView.as_view('graphql', schema=schema, graphiql=True)  # graphiql=True enables the GraphiQL UI for testing
)
from marshmallow import Schema, fields, validate
import graphene
from graphene import ObjectType, Field, List, Int, String, Mutation
from .models import Course as CourseModel, db
from student.models import Student as StudentModel

class CourseInputSchema(Schema):
    name = fields.Str(required=True, validate=validate.Length(min=1, max=128))
    description = fields.Str(required=False, allow_none=True, validate=validate.Length(max=512))
    student_id = fields.Int(required=True)

# Define the CourseType which maps to the Course model
class CourseType(ObjectType):
    id = Int()
    name = String()
    description = String()
    student_id = Int(name="student_id")

# Define StudentType for querying
class StudentType(ObjectType):
    id = Int()
    name = String()
    email = String()
    username = String()

# Define InputType for the mutation
class CourseInput(graphene.InputObjectType):
    name = String(required=True)
    description = String()
    student_id = Int(required=True, name="student_id")

class CreateCourse(Mutation):
    class Arguments:
        course_data = CourseInput(required=True)  # Accept CourseInput as the argument

    course = Field(lambda: CourseType)
    message = String()

    def mutate(self, info, course_data):
        # Check if student exists
        student = StudentModel.query.get(course_data.student_id)
        if not student:
            return CreateCourse(message="Student not found")

        # Create a new Course instance
        course = CourseModel(
            name=course_data.name,
            description=course_data.description,
            student_id=course_data.student_id
        )

        # Add and commit to the database
        db.session.add(course)
        db.session.commit()

        return CreateCourse(course=course, message="Course created successfully")

# Define the Query class to retrieve course data
# class Query(ObjectType):
#     courses = List(CourseType)
#
#     # Resolver function to retrieve course data from the database
#     def resolve_courses(root, info):
#         return CourseModel.query.all()  # Query all courses from the database

# class Query(ObjectType):
#     courses = List(CourseType)
#     course_by_filters = List(CourseType, name=String(), student_id=Int())
#
#     def resolve_courses(root, info):
#         return CourseModel.query.all()
#
#     def resolve_course_by_filters(root, info, name=None, student_id=None):
#         # Start with the base query
#         query = CourseModel.query
#
#         # Apply filters if arguments are provided
#         if name:
#             query = query.filter(CourseModel.name.ilike(f'%{name}%'))
#         if student_id:
#             query = query.filter(CourseModel.student_id == student_id)
#
#         # Execute the query and return results
#         return query.all()

class Query(ObjectType):
    students = List(StudentType)
    courses = List(CourseType, name=String(), student_id=Int())

    def resolve_students(root, info):
        return StudentModel.query.all()

    def resolve_courses(root, info, name=None, student_id=None):
        query = CourseModel.query
        if name:
            query = query.filter(CourseModel.name.ilike(f'%{name}%'))
        if student_id:
            query = query.filter(CourseModel.student_id == student_id)
        return query.all()

# Define Mutation class
class Mutation(ObjectType):
    create_course = CreateCourse.Field()

# Create schema with both Query and Mutation
schema = graphene.Schema(query=Query, mutation=Mutation)
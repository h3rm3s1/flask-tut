from marshmallow import Schema, fields, validate, validates, ValidationError

class StudentSchema(Schema):
    id = fields.Int(dump_only=True)  # Only used for serialization, not for input
    name = fields.Str(required=True, validate=validate.Length(min=1, max=128))
    email = fields.Email(required=True)
    username = fields.Str(required=True, validate=validate.Length(min=3, max=50))
    password = fields.Str(required=True, load_only=True, validate=validate.Length(min=6))

    @validates("username")
    def validate_username(self, value):
        if " " in value:
            raise ValidationError("Username should not contain spaces.")

# Initialize schema instances for use in routes
student_schema = StudentSchema()
students_schema = StudentSchema(many=True)  # For lists of students
"""
Input validation and sanitization utilities to prevent NoSQL injection attacks.
"""

import os
import re
from functools import wraps

from flask import jsonify, request


class ValidationError(Exception):
    """Custom exception for validation errors"""

    def __init__(self, message, field=None):
        self.message = message
        self.field = field
        super().__init__(self.message)


def sanitize_string(value, field_name="field", max_length=1000, allow_empty=False):
    """
    Sanitize and validate string input.
    Prevents NoSQL injection by ensuring the value is a plain string.
    """
    if value is None:
        if allow_empty:
            return None
        raise ValidationError(f"{field_name} is required", field_name)

    if not isinstance(value, str):
        raise ValidationError(f"{field_name} must be a string", field_name)

    value = value.strip()

    if not allow_empty and not value:
        raise ValidationError(f"{field_name} cannot be empty", field_name)

    if len(value) > max_length:
        raise ValidationError(
            f"{field_name} exceeds maximum length of {max_length}", field_name
        )

    if _contains_mongo_operators(value):
        raise ValidationError(f"{field_name} contains invalid characters", field_name)

    return value


def validate_email(value, field_name="email", max_length=254):
    """
    Validate email format and sanitize input.
    """
    value = sanitize_string(value, field_name, max_length)

    email_regex = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"
    if not re.match(email_regex, value):
        raise ValidationError(f"{field_name} must be a valid email address", field_name)

    return value


def validate_otp(value, field_name="otp", max_length=10):
    """
    Validate OTP format (numeric, max length).
    """
    value = sanitize_string(value, field_name, max_length)
    value = validate_integer(value, field_name, min_value=0, max_value=999999)

    return value


def validate_integer(
    value, field_name="value", min_value=None, max_value=None, default=None
):
    """
    Validate and convert a value to integer.
    """
    if value is None:
        if default is not None:
            return default
        raise ValidationError(f"{field_name} is required", field_name)

    try:
        value = int(value)
    except (ValueError, TypeError):
        raise ValidationError(f"{field_name} must be a valid integer", field_name)

    if min_value is not None and value < min_value:
        raise ValidationError(f"{field_name} must be at least {min_value}", field_name)

    if max_value is not None and value > max_value:
        raise ValidationError(f"{field_name} must be at most {max_value}", field_name)

    return value


def validate_boolean(value, field_name="value", default=False):
    """
    Validate and convert a value to boolean.
    """
    if value is None:
        return default

    if isinstance(value, bool):
        return value

    if isinstance(value, str):
        if value.lower() in ("true", "1", "yes"):
            return True
        elif value.lower() in ("false", "0", "no"):
            return False

    raise ValidationError(f"{field_name} must be a boolean", field_name)


def validate_role(value, field_name="role"):
    """
    Validate user role.
    """
    # Fetch allowed roles from environment variable or use defaults
    allowed_roles = os.getenv("ALLOWED_ROLES", "user,admin").split(",")

    if not isinstance(value, str):
        raise ValidationError(f"{field_name} must be a string", field_name)

    value = value.strip()

    if value not in allowed_roles:
        raise ValidationError(f"Given {field_name}={value} is not allowed", field_name)

    return value


def validate_sentiment(value, field_name="sentiment"):
    """
    Validate sentiment value.
    """

    if value is None:
        return ""

    if not isinstance(value, str):
        raise ValidationError(f"{field_name} must be a string", field_name)

    value = value.strip().lower()

    # Allow any non-malicious string for sentiment (flexible)
    if _contains_mongo_operators(value):
        raise ValidationError(f"{field_name} contains invalid characters", field_name)

    return value


def validate_filename(value, field_name="filename"):
    """
    Validate filename for security.
    """
    if value is None:
        raise ValidationError(f"{field_name} is required", field_name)

    if not isinstance(value, str):
        raise ValidationError(f"{field_name} must be a string", field_name)

    value = value.strip()

    if not value:
        raise ValidationError(f"{field_name} cannot be empty", field_name)

    # Prevent directory traversal
    if ".." in value or "/" in value or "\\" in value:
        raise ValidationError(
            f"{field_name} contains invalid path characters", field_name
        )

    # Check for valid filename pattern
    if not re.match(r"^[\w\-. ]+$", value):
        raise ValidationError(f"{field_name} contains invalid characters", field_name)

    return value


def _contains_mongo_operators(value):
    """
    Check if a string contains MongoDB operators that could be used for injection.
    """
    if not isinstance(value, str):
        return True

    # List of MongoDB operators to block
    mongo_operators = [
        "$gt",
        "$gte",
        "$lt",
        "$lte",
        "$ne",
        "$in",
        "$nin",
        "$and",
        "$or",
        "$not",
        "$nor",
        "$exists",
        "$type",
        "$mod",
        "$regex",
        "$text",
        "$where",
        "$all",
        "$elemMatch",
        "$size",
        "$bitsAllClear",
        "$bitsAllSet",
        "$bitsAnyClear",
        "$bitsAnySet",
        "$comment",
        "$expr",
        "$jsonSchema",
        "$meta",
        "$slice",
        "$set",
        "$unset",
        "$inc",
        "$push",
        "$pull",
        "$addToSet",
    ]

    value_lower = value.lower()
    for op in mongo_operators:
        if op in value_lower:
            return True

    return False


# For custom schema-based validation
def sanitize_dict(data, schema):
    """
    Validate and sanitize a dictionary based on a schema.

    Schema format:
    {
        'field_name': {
            'type': 'string' | 'integer' | 'boolean',
            'required': True | False,
            'max_length': int (for strings),
            'min_value': int (for integers),
            'max_value': int (for integers),
            'default': any
        }
    }
    """
    if not isinstance(data, dict):
        raise ValidationError("Request body must be a JSON object")

    result = {}

    for field_name, rules in schema.items():
        value = data.get(field_name)
        field_type = rules.get("type", "string")
        required = rules.get("required", False)

        if value is None and not required:
            if "default" in rules:
                result[field_name] = rules["default"]
            continue

        if field_type == "string":
            result[field_name] = sanitize_string(
                value,
                field_name,
                max_length=rules.get("max_length", 1000),
                allow_empty=not required,
            )
        elif field_type == "integer":
            result[field_name] = validate_integer(
                value,
                field_name,
                min_value=rules.get("min_value"),
                max_value=rules.get("max_value"),
                default=rules.get("default"),
            )
        elif field_type == "boolean":
            result[field_name] = validate_boolean(
                value, field_name, default=rules.get("default", False)
            )
        elif field_type == "role":
            result[field_name] = validate_role(value, field_name)
        elif field_type == "sentiment":
            result[field_name] = validate_sentiment(value, field_name)

    return result


def validate_request(schema):
    """
    Decorator to validate request JSON body against a schema.
    """

    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                data = request.get_json(silent=True) or {}
                validated_data = sanitize_dict(data, schema)
                request.validated_data = validated_data
                return f(*args, **kwargs)
            except ValidationError as e:
                return jsonify({"error": e.message, "field": e.field}), 400

        return decorated_function

    return decorator


def validate_query_params(schema):
    """
    Decorator to validate request query parameters against a schema.
    """

    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                data = dict(request.args)
                validated_data = sanitize_dict(data, schema)
                request.validated_params = validated_data
                return f(*args, **kwargs)
            except ValidationError as e:
                return jsonify({"error": e.message, "field": e.field}), 400

        return decorated_function

    return decorator

import ast
import json
import re

from django.core.exceptions import PermissionDenied
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import IntegrityError
from django.http import Http404
from rest_framework import exceptions
from rest_framework.exceptions import ErrorDetail
from rest_framework.response import Response
from rest_framework.serializers import as_serializer_error
from rest_framework.views import exception_handler

from .exceptions import ApplicationError


def drf_exception_handler(exc, ctx):
    """
    {
        "message": "Error message",
        "extra": {}
    }
    """
    if isinstance(exc, DjangoValidationError):
        exc = exceptions.ValidationError(as_serializer_error(exc))

    if isinstance(exc, Http404):
        exc = exceptions.NotFound()

    if isinstance(exc, PermissionDenied):
        exc = exceptions.PermissionDenied()

    # Handle database constraint violations
    if isinstance(exc, IntegrityError):
        error_message = str(exc)

        # Handle unique constraint violations
        if "unique constraint" in error_message.lower() or "duplicate key" in error_message.lower():
            # Extract table and constraint information
            table_match = re.search(r'"([^"]+)"', error_message)
            constraint_match = re.search(r"Key \(([^)]+)\)=\(([^)]+)\) already exists", error_message)

            if table_match and constraint_match:
                table_match.group(1)
                fields = constraint_match.group(1)
                values = constraint_match.group(2)

                # Provide user-friendly message based on table

                message = f"A record with {fields}={values} already exists"
            else:
                message = "A record with these details already exists"
        else:
            message = "Database constraint violation occurred"

        exc = exceptions.ValidationError(message)

    response = exception_handler(exc, ctx)

    # If unexpected error occurs (server error, etc.)
    if response is None:
        if isinstance(exc, ApplicationError):
            data = {"message": str(exc.message), "extra": exc.extra}
            return Response(data, status=400)
        # For any other unexpected exception, return a JSON response
        # This ensures no HTML pages are ever returned
        error_message = str(exc) if exc else "An unexpected error occurred"
        return Response(
            {"message": error_message, "extra": {"exception_type": type(exc).__name__}},
            status=500,
        )

    def extract_first_message(obj):
        # Recursively extract the first string message from obj
        if isinstance(obj, ErrorDetail):
            return str(obj)
        if isinstance(obj, list):
            for item in obj:
                msg = extract_first_message(item)
                if msg and msg != "Unknown error":
                    return msg
            return "Unknown error"
        if isinstance(obj, dict):
            for v in obj.values():
                msg = extract_first_message(v)
                if msg and msg != "Unknown error":
                    return msg
            return "Unknown error"
        if isinstance(obj, str):
            return obj
        return "Unknown error"

    def is_field_validation_error(obj):
        # Check if this is a field-level validation error (dict with field names as keys)
        if isinstance(obj, dict):
            # Check if values are lists (typical for field validation errors)
            return any(isinstance(v, list) for v in obj.values())
        return False

    def parse_string_to_dict(string_obj):
        """Try to parse a string representation of a dict back to a dict"""
        if not isinstance(string_obj, str):
            return string_obj

        try:
            # Handle the specific format: "{'description': [ErrorDetail(string='This field is required.', code='required')]}"  # noqa: E501
            if string_obj.startswith("{") and string_obj.endswith("}"):
                # First, convert ErrorDetail objects to a parseable format
                # Replace ErrorDetail objects with a simple dict representation
                error_detail_pattern = r"ErrorDetail\(string='([^']+)', code='([^']+)'\)"

                def replace_error_detail(match):
                    string_val = match.group(1)
                    code_val = match.group(2)
                    return f'{{"string": "{string_val}", "code": "{code_val}"}}'

                # Replace all ErrorDetail objects in the string
                cleaned_string = re.sub(error_detail_pattern, replace_error_detail, string_obj)

                # Now try to parse the cleaned string
                try:
                    # Use ast.literal_eval to safely evaluate the string
                    return ast.literal_eval(cleaned_string)
                except (ValueError, SyntaxError):
                    # If that fails, try JSON parsing
                    json_string = cleaned_string.replace("'", '"')
                    return json.loads(json_string)
        except (ValueError, SyntaxError, json.JSONDecodeError):
            pass
        return string_obj

    detail = None
    if hasattr(response, "data"):
        data = response.data
        if isinstance(data, dict) and "detail" in data:
            detail = data["detail"]
        else:
            detail = data
    else:
        detail = None

    # Try to parse if detail is a string representation of a dict
    if isinstance(detail, str):
        detail = parse_string_to_dict(detail)

    message = extract_first_message(detail)
    extra = {}

    # Handle field-level validation errors
    if detail and is_field_validation_error(detail):
        extra = {"fields": detail}
        # Create a more generic message for field validation errors
        if isinstance(detail, dict):
            field_names = list(detail.keys())
            if len(field_names) == 1:
                message = f"Validation error in field '{field_names[0]}'"
            else:
                message = f"Validation errors in fields: {', '.join(field_names)}"
    elif detail and not isinstance(detail, (str, ErrorDetail)):
        # For other non-string, non-ErrorDetail objects
        extra = {"detail": detail}

    response.data = {"message": message, "extra": extra}
    return response

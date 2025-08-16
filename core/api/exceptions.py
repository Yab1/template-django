import logging
import re

from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import IntegrityError
from rest_framework.exceptions import NotFound, ValidationError

logger = logging.getLogger(__name__)


class ApplicationError(Exception):
    def __init__(self, message, extra=None):
        super().__init__(message)
        self.message = message
        self.extra = extra or {}


class BusinessLogicError(ApplicationError):
    pass


class ResourceNotFoundError(ApplicationError):
    pass


class PermissionError(ApplicationError):
    pass


class InvalidStateError(ApplicationError):
    pass


def handle_api_exception(exception, operation_name="operation"):
    """
    Centralized exception handler for API operations.
    Handles all common exception types and returns the appropriate exception to raise.

    Args:
        exception: The caught exception
        operation_name: Name of the operation for generic error messages

    Returns:
        Exception to raise (either the original or a converted one)
    """
    # Log the exception for debugging
    logger.error(f"Exception in {operation_name}: {str(exception)}")

    # Handle database constraint violations
    if isinstance(exception, IntegrityError):
        error_message = str(exception)

        # Handle unique constraint violations
        if "unique constraint" in error_message.lower() or "duplicate key" in error_message.lower():
            # Extract table and constraint information
            table_match = re.search(r'"([^"]+)"', error_message)
            constraint_match = re.search(r"Key \(([^)]+)\)=\(([^)]+)\) already exists", error_message)

            if table_match and constraint_match:
                table_match.group(1)
                fields = constraint_match.group(1)
                values = constraint_match.group(2)

                return ValidationError(f"A record with {fields}={values} already exists")
            return ValidationError("A record with these details already exists")

        # Handle other constraint violations
        if "not null" in error_message.lower():
            return ValidationError("Required field is missing")
        if "foreign key" in error_message.lower():
            return ValidationError("Referenced record does not exist")
        return ValidationError("Database constraint violation occurred")

    # Handle specific exception types
    if isinstance(exception, (ValidationError, DjangoValidationError)):
        # Re-raise validation errors as-is
        return exception

    if isinstance(exception, (ApplicationError, BusinessLogicError, InvalidStateError)):
        # Re-raise custom application errors as-is
        return exception

    if isinstance(exception, ResourceNotFoundError):
        # Convert to DRF NotFound
        return NotFound(str(exception))

    # For any other unexpected exception, wrap in ApplicationError
    # This ensures JSON response instead of HTML
    return ApplicationError(f"Failed to {operation_name}: {str(exception)}")

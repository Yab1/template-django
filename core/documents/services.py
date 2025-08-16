import os
import uuid
from typing import Any, Dict, Optional

from django.contrib.contenttypes.models import ContentType
from django.db import transaction

from .models import Document


def get_processed_filename(original_filename: str) -> str:
    # Get file extension
    _, ext = os.path.splitext(original_filename)

    # Convert original filename to snake case (without extension)
    name_without_ext = os.path.splitext(original_filename)[0]
    snake_case_name = name_without_ext.lower().replace(" ", "_")

    # Add UUID
    return f"{snake_case_name}_{uuid.uuid4().hex[:8]}{ext}"


def cleanup_document_data(request_data: Dict[str, Any], files_data=None, file_key="document") -> Dict[str, Any]:
    """
    Clean up document data from request by stripping whitespace from string fields
    and handling any other necessary data transformations.

    Args:
        request_data: The request data dictionary
        files_data: Optional FILES data dictionary
        file_key: The key to use for the file in files_data

    Returns:
        Dict with cleaned data
    """
    cleaned_data = {}

    # Log the incoming data for debugging

    # Handle different request data formats
    # For multipart form data, Django puts everything in request.data as QueryDict
    # For JSON data, we need to extract fields from request.data

    # Helper function to get value from request_data, handling QueryDict specially
    def get_value(key):
        if hasattr(request_data, "getlist"):
            # This is a QueryDict
            values = request_data.getlist(key)
            if len(values) == 1:
                return values[0]
            if len(values) > 1:
                return values
            return None
        # Regular dict
        return request_data.get(key)

    # Clean up document_type if present
    if "document_type" in request_data:
        value = get_value("document_type")
        if value is not None and hasattr(value, "strip"):
            cleaned_data["document_type"] = value.strip()
        else:
            cleaned_data["document_type"] = value

    # Pass document file from files_data if provided
    if files_data and file_key in files_data:
        cleaned_data["document"] = files_data[file_key]
    elif "document" in request_data:
        # This handles the case where document is in request.data (for non-multipart requests)
        cleaned_data["document"] = get_value("document")

    # Clean up entity_type if present
    if "entity_type" in request_data:
        value = get_value("entity_type")
        if value is not None and hasattr(value, "strip"):
            cleaned_data["entity_type"] = value.strip()
        else:
            cleaned_data["entity_type"] = value

    # Clean up entity_id if present
    if "entity_id" in request_data:
        value = get_value("entity_id")
        if value is not None and hasattr(value, "strip"):
            cleaned_data["entity_id"] = value.strip()
        else:
            cleaned_data["entity_id"] = value

    return cleaned_data


@transaction.atomic
def document_upload(
    validated_data: dict,
    user,
) -> tuple[Optional[Document], Optional[str]]:
    try:
        # Validate entity type exists in Django's content types
        try:
            content_type = ContentType.objects.get(
                model=validated_data["entity_type"].lower(),
            )
        except ContentType.DoesNotExist:
            return None, f"Invalid entity type: {validated_data["entity_type"]}"

        # Get the uploaded file and process its name
        uploaded_file = validated_data["document"]
        processed_filename = get_processed_filename(uploaded_file.name)

        # Convert UUID to string for object_id
        entity_id = str(validated_data["entity_id"])

        # Create document
        document = Document.objects.create(
            content_type=content_type,
            object_id=entity_id,  # Store UUID as string
            document_type=validated_data["document_type"],
            document_name=processed_filename,
            document_path=uploaded_file,
            uploaded_by=user,
        )

        return document, None

    except Exception as e:
        return None, f"Error processing document: {str(e)}"


@transaction.atomic
def document_update(
    document: Document,
    validated_data: dict,
    user,
) -> tuple[Optional[Document], Optional[str]]:
    try:
        # Update entity type if provided
        if "entity_type" in validated_data:
            try:
                content_type = ContentType.objects.get(
                    model=validated_data["entity_type"].lower(),
                )
                document.content_type = content_type
            except ContentType.DoesNotExist:
                return None, f"Invalid entity type: {validated_data["entity_type"]}"

        # Update entity_id if provided
        if "entity_id" in validated_data:
            document.object_id = str(validated_data["entity_id"])

        # Update document_type if provided
        if "document_type" in validated_data:
            document.document_type = validated_data["document_type"]

        # Update document file if provided
        if "document" in validated_data:
            # Get the uploaded file and process its name
            uploaded_file = validated_data["document"]
            processed_filename = get_processed_filename(uploaded_file.name)

            # Update document fields
            document.document_name = processed_filename
            document.document_path = uploaded_file

        # Update uploaded_by
        document.uploaded_by = user

        # Save the document
        document.save()

        return document, None

    except Exception as e:
        return None, f"Error updating document: {str(e)}"


def upload_documents_from_raw_request(*, user, raw_request_data, files_data, entity_type, entity_id):
    """
    Upload multiple documents from raw request data for a given entity type and entity id.
    Returns a tuple: (list of created documents, list of errors)
    """
    documents_data = []
    i = 0
    while True:
        prefix = f"documents[{i}]"
        if f"{prefix}[document_type]" not in raw_request_data:
            break

        # Prepare raw data for this document
        raw_doc_data = {
            "document_type": raw_request_data.get(f"{prefix}[document_type]"),
            "entity_type": entity_type,
            "entity_id": entity_id,
        }
        file_key = prefix  # The file is in files_data as 'documents[0]', 'documents[1]', etc.

        # Clean up the data using the shared service
        doc_data = cleanup_document_data(raw_doc_data, files_data, file_key)
        documents_data.append(doc_data)
        i += 1

    created_documents = []
    errors = []
    for doc_data in documents_data:
        document, error = document_upload(doc_data, user)
        if error:
            errors.append(error)
            continue
        created_documents.append(document)
    return created_documents, errors

from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models

from config.env import env
from core.common.models import BaseModel


def document_upload_path(instance, filename):
    """
    Determine the upload path for documents based on year, entity type, object ID, and document type.
    This creates a directory structure like:
    2024/documents/provider/123e4567-e89b-12d3-a456-426614174000/medical_license/filename.pdf
    """
    # Get current year
    import datetime

    current_year = datetime.datetime.now().year

    # Get the entity type (provider, patient, etc.)
    entity_type = "unknown"
    if hasattr(instance, "content_type") and instance.content_type:
        entity_type = instance.content_type.model

    # Get the object ID
    object_id = "unknown"
    if hasattr(instance, "object_id") and instance.object_id:
        object_id = str(instance.object_id)

    # Get the document type and convert to a path-friendly format
    doc_type = "unknown"
    if hasattr(instance, "document_type") and instance.document_type:
        doc_type = instance.document_type.lower().replace(" ", "_")

    # Create path: year/documents/entity_type/object_id/doc_type/filename
    return f"{current_year}/documents/{entity_type}/{object_id}/{doc_type}/{filename}"


class Document(BaseModel):
    class DocumentType(models.TextChoices):
        PROFILE_PICTURE = "profile_picture", "Profile Picture"
        OTHER = "other", "Other"

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.UUIDField()
    entity = GenericForeignKey("content_type", "object_id")
    document_type = models.CharField(max_length=255, choices=DocumentType.choices)
    document_name = models.CharField(max_length=255)
    document_path = models.FileField(upload_to=document_upload_path)
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.document_type} - {self.document_name}"

    @property
    def document_full_path(self) -> str:
        return f"{env.str('MEDIA_STORAGE_ENDPOINT')}{self.document_path}"

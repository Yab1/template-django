from django.contrib.contenttypes.models import ContentType

from .models import Document


def document_get_by_entity(*, entity_type, entity_id: str):
    """Return documents linked to an entity.

    Accepts either a model class/instance or a string model name for entity_type.
    """
    if isinstance(entity_type, str):
        # entity_type provided as model name (case-insensitive)
        content_type = ContentType.objects.get(model=entity_type.lower())
    else:
        # entity_type provided as model class/instance
        content_type = ContentType.objects.get_for_model(entity_type)

    return Document.objects.filter(content_type=content_type, object_id=entity_id)

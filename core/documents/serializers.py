from rest_framework import serializers

from core.users.serializers import UserSummarySerializer


class DocumentOutputSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    document_type = serializers.CharField()
    document_name = serializers.CharField()
    document_path = serializers.CharField()
    document_full_path = serializers.CharField()
    uploaded_by = UserSummarySerializer()
    created_at = serializers.DateTimeField()
    updated_at = serializers.DateTimeField()

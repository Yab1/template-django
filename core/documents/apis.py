import logging

from django.shortcuts import get_object_or_404
from drf_yasg.utils import swagger_auto_schema
from rest_framework import serializers, status
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from core.api.mixins import ApiAuthMixin
from core.common.utils import get_object, inline_serializer

from .models import Document
from .services import cleanup_document_data, document_update, document_upload

logger = logging.getLogger(__name__)


class DocumentsUpload(ApiAuthMixin, APIView):
    class InputSerializer(serializers.Serializer):
        documents = inline_serializer(
            name="DocumentDataSerializer",
            many=True,
            fields={
                "document_type": serializers.ChoiceField(
                    choices=Document.DOCUMENT_CHOICES,
                ),
                "document": serializers.FileField(),
                "entity_type": serializers.CharField(),
                "entity_id": serializers.UUIDField(),
            },
        )

        class Meta:
            ref_name = "DocumentUploadInputSerializer"

    class OutputDocumentSerializer(serializers.Serializer):
        id = serializers.UUIDField()
        document_type = serializers.CharField()
        document_name = serializers.CharField()
        document_path = serializers.CharField()
        created_at = serializers.DateTimeField()
        updated_at = serializers.DateTimeField()

        class Meta:
            ref_name = "DocumentUploadOutputSerializer"

    @swagger_auto_schema(
        request_body=InputSerializer,
        responses={200: OutputDocumentSerializer(many=True)},
        tags=["Documents"],
        operation_summary="Upload documents",
        operation_id="upload_documents",
    )
    def post(self, request, *args, **kwargs):
        try:
            # Manually construct the data format
            documents_data = []
            i = 0
            while True:
                prefix = f"documents[{i}]"
                if f"{prefix}[document_type]" not in request.data:
                    break

                # Get raw data
                raw_doc_data = {
                    "document_type": request.data.get(f"{prefix}[document_type]"),
                    "entity_type": request.data.get(f"{prefix}[entity_type]"),
                    "entity_id": request.data.get(f"{prefix}[entity_id]"),
                }

                # Clean up the data with specific file key
                file_key = f"{prefix}[document]"
                doc_data = cleanup_document_data(raw_doc_data, request.FILES, file_key)

                documents_data.append(doc_data)
                i += 1

            input_serializer = self.InputSerializer(data={"documents": documents_data})
            input_serializer.is_valid(raise_exception=True)

            created_documents = []
            errors = []

            for doc_data in input_serializer.validated_data["documents"]:
                document, error = document_upload(doc_data, request.user)

                if error:
                    errors.append(error)
                    continue

                output_serializer = self.OutputDocumentSerializer(document)
                created_documents.append(output_serializer.data)

            response_data = {"created_documents": created_documents, "errors": errors}

            if not created_documents and errors:
                return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

            return Response(response_data, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )


class DocumentUpdate(ApiAuthMixin, APIView):
    parser_classes = (MultiPartParser, FormParser, JSONParser)

    class InputSerializer(serializers.Serializer):
        document_type = serializers.ChoiceField(choices=Document.DOCUMENT_CHOICES, required=False)
        document = serializers.FileField(required=False)
        entity_type = serializers.CharField(required=False)
        entity_id = serializers.UUIDField(required=False)

        class Meta:
            ref_name = "DocumentUpdateInputSerializer"

    class OutputDocumentSerializer(serializers.Serializer):
        id = serializers.UUIDField()
        document_type = serializers.CharField()
        document_name = serializers.CharField()
        document_path = serializers.CharField()
        created_at = serializers.DateTimeField()
        updated_at = serializers.DateTimeField()

        class Meta:
            ref_name = "DocumentUpdateOutputSerializer"

    @swagger_auto_schema(
        request_body=InputSerializer,
        responses={200: OutputDocumentSerializer},
        tags=["Documents"],
        operation_summary="Update a document",
        operation_id="update_document",
    )
    def patch(self, request, document_id, *args, **kwargs):
        try:
            document = get_object(Document, id=document_id)

            # Log raw request data for debugging
            logger.info(f"Request data: {request.data}")
            logger.info(f"Request FILES: {request.FILES}")
            logger.info(f"Request content type: {request.content_type}")

            # Clean up the input data using the service - pass the raw request data
            cleaned_data = cleanup_document_data(request.data, request.FILES)

            logger.info(f"Cleaned data: {cleaned_data}")

            # Validate input data
            serializer = self.InputSerializer(data=cleaned_data)
            serializer.is_valid(raise_exception=True)

            logger.info(f"Validated data: {serializer.validated_data}")

            # Update document using service
            updated_document, error = document_update(
                document=document,
                validated_data=serializer.validated_data,
                user=request.user,
            )

            if error:
                logger.error(f"Error updating document: {error}")
                return Response({"error": error}, status=status.HTTP_400_BAD_REQUEST)

            # Serialize and return the updated document
            output_serializer = self.OutputDocumentSerializer(updated_document)
            return Response(output_serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            logger.exception(f"Error updating document: {str(e)}")
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class DocumentDelete(ApiAuthMixin, APIView):
    class OutputSerializer(serializers.Serializer):
        message = serializers.CharField()

        class Meta:
            ref_name = "DocumentDeleteOutputSerializer"

    @swagger_auto_schema(
        responses={200: OutputSerializer},
        tags=["Documents"],
        operation_summary="Delete a document",
        operation_id="delete_document",
    )
    def delete(self, request, document_id, *args, **kwargs):
        try:
            document = get_object_or_404(Document, id=document_id)

            # Delete the document
            document.delete()

            return Response(
                {"message": "Document deleted successfully"},
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class DocumentApiView(APIView):
    @swagger_auto_schema(
        request_body=DocumentsUpload.InputSerializer,
        responses={200: DocumentsUpload.OutputDocumentSerializer(many=True)},
        tags=["Documents"],
        operation_summary="Upload documents",
        operation_id="upload_documents",
    )
    def post(self, request, *args, **kwargs):
        view = DocumentsUpload.as_view()
        return view(request._request, *args, **kwargs)

    @swagger_auto_schema(
        responses={200: DocumentDelete.OutputSerializer},
        tags=["Documents"],
        operation_summary="Delete document",
        operation_id="delete_document",
    )
    def delete(self, request, document_id, *args, **kwargs):
        view = DocumentDelete.as_view()
        return view(request._request, document_id, *args, **kwargs)


class DocumentByIdApiView(ApiAuthMixin, APIView):
    parser_classes = (MultiPartParser, FormParser, JSONParser)

    @swagger_auto_schema(
        request_body=DocumentUpdate.InputSerializer,
        responses={200: DocumentUpdate.OutputDocumentSerializer},
        tags=["Documents"],
        operation_summary="Update document",
        operation_id="update_document",
    )
    def patch(self, request, document_id, *args, **kwargs):
        view = DocumentUpdate.as_view()
        return view(request._request, document_id, *args, **kwargs)

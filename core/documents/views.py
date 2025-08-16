from django.contrib.contenttypes.models import ContentType
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Document
from .serializers import DocumentSerializer


class DocumentViewSet(viewsets.ModelViewSet):
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=["POST"])
    def upload_multiple(self, request):
        """
        Upload multiple documents at once.
        Expected payload format:
        {
            "documents": [
                {
                    "document_type": "Medical License",
                    "document_name": "license.pdf",
                    "document_path": <file>,
                    "content_type": "doctor",  # app label
                    "object_id": 1
                },
                ...
            ]
        }
        """
        documents_data = request.data.get("documents", [])
        if not documents_data:
            return Response(
                {"error": "No documents provided"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        created_documents = []
        errors = []

        for doc_data in documents_data:
            try:
                # Get content type
                content_type = ContentType.objects.get(
                    model=doc_data.get("content_type").lower(),
                )

                # Create document instance
                document = Document(
                    content_type=content_type,
                    object_id=doc_data.get("object_id"),
                    document_type=doc_data.get("document_type"),
                    document_name=doc_data.get("document_name"),
                    document_path=doc_data.get("document_path"),
                    uploaded_by=request.user,
                )
                document.save()

                serializer = self.get_serializer(document)
                created_documents.append(serializer.data)

            except ContentType.DoesNotExist:
                errors.append(f"Invalid content type: {doc_data.get("content_type")}")
            except Exception as e:
                errors.append(f"Error processing document {doc_data.get("document_name")}: {str(e)}")

        response_data = {
            "created_documents": created_documents,
            "errors": errors,
        }

        status_code = status.HTTP_201_CREATED if created_documents else status.HTTP_400_BAD_REQUEST
        return Response(response_data, status=status_code)

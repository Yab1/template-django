from django.urls import path

from .apis import DocumentApiView, DocumentByIdApiView

urlpatterns = [
    path("", DocumentApiView.as_view(), name="documents"),
    path("<uuid:document_id>/", DocumentByIdApiView.as_view(), name="document_operations"),
]

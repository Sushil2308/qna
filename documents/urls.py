from django.urls import path
from documents.views import DocumentIngestion

urlpatterns = [
    path(
        "ingestion",
        DocumentIngestion.as_view(),
        name="Docuemnt Ingestion Operations",
    )
]

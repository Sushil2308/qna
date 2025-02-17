from django.urls import path
from docops.views import DocumentIngestion

urlpatterns = [
    path(
        "ingestion",
        DocumentIngestion.as_view(),
        name="Docuemnt Ingestion Operations",
    )
]
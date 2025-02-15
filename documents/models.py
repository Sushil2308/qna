from django.db import models
from uuid import uuid4
from django.contrib.auth.models import User

class ProcessStatus(models.Model):
    status = models.CharField(max_length=20, null=False, unique=True)
    createdAt = models.DateTimeField(auto_now_add=True)


class DocumentInfo(models.Model):
    """Stores the full document metadata."""
    documentUUID = models.UUIDField(unique=True, default=uuid4, null=False)
    documentTitle = models.CharField(max_length=255)
    user = models.ForeignKey(User, null=False, on_delete=models.DO_NOTHING, help_text="Who uploaded this file")
    createdAt = models.DateTimeField(auto_now_add=True, help_text="Document Uploaded Date Time")
    updatedAt = models.DateTimeField(auto_now=True, help_text="Document Last Updated Date Time")
    chunkedOn = models.DateTimeField(null=True, help_text="Document Chunked Date Time")
    processStatus = models.ForeignKey(
        ProcessStatus,
        null=False,
        on_delete=models.DO_NOTHING,
        help_text="Current Status of Document Chunking"
    )
    def __str__(self):
        return self.documentTitle


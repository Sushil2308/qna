from django.db import models
from django.contrib.auth.models import User
from uuid import uuid4
from documents.models import DocumentInfo

class ChatSessionManager(models.Model):
    sessionUUID =  models.UUIDField(default=uuid4, unique=True, null=False)
    user = models.ForeignKey(
        User,
        null=False,
        on_delete=models.DO_NOTHING,
        help_text= "Chat Session Initiated by which User"
    )
    sessionStatus = models.BooleanField(default=False, help_text="Current Session Status")
    sessionCreatedOn = models.DateTimeField(auto_now_add=True, help_text="When the session was created")
    sessionLastAccessedOn = models.DateTimeField(auto_now=True, help_text="Session Last Accessed On")

class SessionDocumentInfo(models.Model):
    chatSession = models.ForeignKey(
        ChatSessionManager,
        null=False,
        on_delete=models.DO_NOTHING,
        help_text="Document Related to Which Session"
    )
    document = models.ForeignKey(
        DocumentInfo,
        null=False,
        on_delete=models.DO_NOTHING,
        help_text="Document Info of the given Session"
    )
    canParticipate = models.BooleanField(default=True, help_text="Need to add this document while given answer to the user")
    documentAddedOn = models.DateTimeField(auto_now_add=True, help_text="When the document was added to the session")
    documentUpdatedOn = models.DateTimeField(auto_now=True, help_text="When the last document was updated")

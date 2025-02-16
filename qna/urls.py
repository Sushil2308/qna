from django.urls import path
from qna.views import SessionManager


urlpatterns = [
    path("session/", SessionManager.as_view(), name="Session Create and Update Status")
]

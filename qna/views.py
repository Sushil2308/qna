from adrf.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from uuid import uuid4
from django.core.exceptions import ObjectDoesNotExist
from qna.models import ChatSessionManager, SessionDocumentInfo, DocumentInfo


class SessionManager(APIView):
    """Manages chat sessions and associated documents."""

    permission_classes = [IsAuthenticated]

    async def post(self, request):
        """Creates a new chat session without any documents initially."""
        try:
            user = request.user
            # Create a new chat session
            session_uuid = uuid4()
            session = await ChatSessionManager.objects.acreate(
                sessionUUID=session_uuid, user=user, sessionStatus=True
            )
            return Response(
                {
                    "message": "Session created successfully.",
                    "sessionUUID": str(session.sessionUUID),
                },
                status=status.HTTP_201_CREATED,
            )

        except Exception as e:
            return Response(
                {"error": f"An internal error occurred: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    async def put(self, request):
        """Adds new documentUUIDs to an existing session."""
        try:

            user = request.user
            data = request.data
            document_uuids = data.get("documentUUIDs", [])
            sessionUUID = data.get("sessionUUID")

            if not sessionUUID:
                return Response(
                    {"error": "No sessionUUID provided."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if not document_uuids:
                return Response(
                    {"error": "No documentUUIDs provided."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Check if the session exists and belongs to the user
            try:
                session = await ChatSessionManager.objects.aget(
                    sessionUUID=sessionUUID, user=user
                )
            except ObjectDoesNotExist:
                return Response(
                    {"error": "Session not found or unauthorized."},
                    status=status.HTTP_404_NOT_FOUND,
                )

            # Fetch only valid documentUUIDs that belong to the user
            existing_documents = {
                str(doc["documentUUID"]): doc["id"]
                async for doc in DocumentInfo.objects.filter(
                    documentUUID__in=document_uuids, user=user
                ).values("documentUUID", "id")
            }

            # Identify invalid documentUUIDs
            invalid_uuids = set(document_uuids) - set(existing_documents.keys())
            if invalid_uuids:
                return Response(
                    {"error": f"Invalid documentUUIDs: {list(invalid_uuids)}"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Check for already linked documents
            existing_session_docs = {
                str(doc)
                async for doc in SessionDocumentInfo.objects.filter(
                    chatSession=session, document__documentUUID__in=document_uuids
                ).values_list("document__documentUUID", flat=True)
            }

            new_docs = [
                SessionDocumentInfo(
                    chatSession=session,
                    document_id=existing_documents[doc_uuid],
                    canParticipate=True,
                )
                for doc_uuid in set(existing_documents.keys())
                - set(existing_session_docs)
            ]

            # Add only new documents to the session
            if new_docs:
                await SessionDocumentInfo.objects.abulk_create(new_docs)

            return Response(
                {
                    "message": "Documents added to session successfully.",
                    "sessionUUID": str(session.sessionUUID),
                    "documentUUIDs": document_uuids,
                },
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            return Response(
                {"error": f"An internal error occurred: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

from adrf.views import APIView
from rest_framework.response import Response 
from rest_framework.permissions import IsAuthenticated 
from documents.management.commands import DocumentSplitter
from uuid import uuid4 
from aisolution.settings import COLLECTION_DB 
from documents.models import DocumentInfo, ProcessStatus 
from django.core.exceptions import ObjectDoesNotExist 
from rest_framework import status 
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

class DocumentIngestion(APIView, DocumentSplitter):
    permission_classes = [IsAuthenticated]  # Ensures only authenticated users can access this endpoint

    async def get(self, request):
        """
        Handles retrieving a paginated list of documents for the authenticated user.
        """
        try:
            # Extracts pagination parameters from the request, defaulting to 10 items per page
            perPage = request.GET.get('perPage', 10)
            page_number = request.GET.get('page')

            # Asynchronously fetches documents belonging to the user, selecting specific fields
            documents = [document async for document in DocumentInfo.objects.filter(user=request.user)
                         .values("documentUUID", "documentTitle", "processStatus__status", "createdAt")]

            # Initializes Django's Paginator with the retrieved documents
            paginator = Paginator(documents, perPage)

            try:
                # Fetches the requested page
                paginated_queryset = paginator.page(page_number)
            except PageNotAnInteger:
                # Defaults to the first page if the page number is not an integer
                paginated_queryset = paginator.page(1)
            except EmptyPage:
                # Returns an error if the page number is out of range
                return Response({"error": "No more pages"}, status=404)

            # Constructs and returns the paginated response
            return Response({
                "count": paginator.count,  # Total number of documents
                "total_pages": paginator.num_pages,  # Total number of pages
                "current_page": page_number,  # Current page number
                "next_page": paginated_queryset.next_page_number() if paginated_queryset.has_next() else None,
                "previous_page": paginated_queryset.previous_page_number() if paginated_queryset.has_previous() else None,
                "results": list(paginated_queryset)  # List of documents for the current page
            })
        except Exception as e:
            print(str(e))  # Logs the error
            return Response({"error": "An internal error occurred."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    
    async def post(self, request):
        """
        Handles document ingestion by saving metadata in the database and storing content in Weaviate.
        """
        try:
            uploaded_Content = request.data  # Retrieves uploaded document content from the request
        
            # Attempts to retrieve the 'In Process' status for document processing
            try:
                scheduled_status = await ProcessStatus.objects.aget(status="In Process")
            except ObjectDoesNotExist:
                # Returns an error if the required status is missing
                return Response({"error": "Scheduled status not found."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            # Creates a new DocumentInfo record asynchronously
            docOB = await DocumentInfo.objects.acreate(
                documentUUID=uuid4(),  # Generates a unique identifier for the document
                user_id=request.user.id,  # Associates the document with the authenticated user
                processStatus=scheduled_status,  # Assigns the 'In Process' status
                documentTitle=uploaded_Content["name"]  # Stores the document title
            )

            # Stores the document content in Weaviate for vector search capabilities
            message = await self.store_in_weaviate(text=uploaded_Content["text"], docOB=docOB, source=COLLECTION_DB)

            # Returns a success response with the ingestion status and document UUID
            return Response({"message": {"IngestionStatus": message, "DocumentUUID": docOB.documentUUID}}, 
                            status=status.HTTP_201_CREATED)

        except Exception as e:
            # Logs the error and returns a generic internal server error response
            return Response({"error": "An internal error occurred."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

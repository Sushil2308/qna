from adrf.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from documents.management.commands import DocumentSplitter
from uuid import uuid4
from aisolution.settings import COLLECTION_DB

class DocumentIngestion(APIView, DocumentSplitter):
    permission_classes = [IsAuthenticated]

    async def get(self, request):
        return Response({"message": "You are authenticated!", "user": request.user.username})
    
    async def post(self, request):
        chunks = await self.process_pdf(filename="/Users/shtlpmac006/Desktop/MovedFiles/solutionhub/aisolution/SushilResume.pdf")
        print(chunks)
        return Response({"message": await self.store_in_weaviate(chunks=chunks, documentUUID=uuid4(), source=COLLECTION_DB)})


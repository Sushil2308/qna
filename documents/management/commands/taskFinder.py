import asyncio
from django.core.management.base import BaseCommand 
from aisolution.settings import TASK_QUEUE, TASK_LOCK
from documents.models import DocumentInfo, ProcessStatus

class Command(BaseCommand):
    help = "Check the database every 5 seconds for in-process documents and load tasks into central async queue."
    
    async def check_documents(self, batch_size=10):
        inProcessID = ProcessStatus.objects.get(status = "In Process").pk
        scheduledID = ProcessStatus.objects.get(status = "Scheduled").pk
        while True:
            async for document in DocumentInfo.objects.filter(processStatus_id = scheduledID)[:batch_size]:
                async with TASK_LOCK:
                    document.processStatus_id = inProcessID
                    await TASK_QUEUE.put(document.documentUUID)
                    await document.asave(update_fields=["processStatus", "updatedAt"])
                    self.stdout.write(self.style.SUCCESS(f"Loaded document {document.documentUUID} into central async queue."))
            await asyncio.sleep(5)

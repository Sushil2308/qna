import weaviate
from weaviate.classes.init import Auth
from llm.logic import ChunkEmbedding
import weaviate.classes as wvc
from aisolution.settings import WEAVIATE_HOST, WEAVIATE_PASSWORD
from documents.models import DocumentInfo, ProcessStatus
from datetime import datetime
from .splitterConfig import TextChunker
CHUNKER = TextChunker()

class DocumentSplitter(ChunkEmbedding):

    async def store_in_weaviate(self, text: str, source: str, docOB: DocumentInfo) -> str:
        """
        Asynchronously processes a document by chunking its text, generating embeddings, and storing the chunks in Weaviate.
        Updates the document's processing status accordingly.
        """
        try:
            # Step 1: Chunk the text
            chunks = await CHUNKER.getChunks(text=text)

            # Step 2: Initialize an asynchronous Weaviate client
            weaviate_client = weaviate.use_async_with_weaviate_cloud(
                cluster_url=WEAVIATE_HOST, 
                auth_credentials=Auth.api_key(WEAVIATE_PASSWORD)
            )

            # Step 3: Attempt to connect to Weaviate
            await weaviate_client.connect()

            # Step 4: Ensure the client is properly initialized and connected
            if not weaviate_client:
                raise ValueError("Weaviate client is not initialized!")
            if not weaviate_client.is_connected():
                raise ValueError("Weaviate client is not able to connect!")

            # Step 5: Generate vector embeddings for each chunk
            chunksVector = await self.aembedding(chunks=chunks)

            # Step 6: Update the document's chunking timestamp
            docOB.chunkedOn = datetime.now()

            # Step 7: Prepare chunk data for insertion into Weaviate
            async with weaviate_client as client:
                data_objects = [
                    wvc.data.DataObject(
                        properties={
                            "textChunk": chunk,       # The chunked text
                            "chunkRank": i + 1,       # Rank order of the chunk
                            "documentUUID": docOB.documentUUID  # Associate chunk with document
                        },
                        vector=chunksVector[i]  # Corresponding embedding vector
                    )
                    for i, chunk in enumerate(chunks)
                ]

                # Step 8: Retrieve the appropriate Weaviate collection
                collection = client.collections.get(source)

                # Step 9: Insert all chunks into the Weaviate collection
                await collection.data.insert_many(data_objects)

            # Step 10: Update the document's processing status to "Success" and save changes
            docOB.processStatus = await ProcessStatus.objects.aget(status="Success")
            await docOB.asave(update_fields=["chunkedOn", "processStatus", "updatedAt"])

            # Step 11: Close the Weaviate connection
            await weaviate_client.close()

            return f"Successfully stored {len(chunks)} chunks in Weaviate!"
        
        except Exception as e:
            # Step 12: If an error occurs, update the document's processing status to "Failed" and save changes
            docOB.processStatus = await ProcessStatus.objects.aget(status="Failed")
            await docOB.asave()

            # Step 13: Raise the exception so it can be logged or handled externally
            raise Exception(e)

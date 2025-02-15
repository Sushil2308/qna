import weaviate
import re
from unstructured.partition.auto import partition
from asgiref.sync import sync_to_async
from aisolution.settings import CHUNK_SIZE, OVERLAP
from weaviate.classes.init import Auth
from llm.logic import ChunkEmbedding
import weaviate.classes as wvc
from aisolution.settings import WEAVIATE_HOST, WEAVIATE_PASSWORD
class DocumentSplitter(ChunkEmbedding):

    @sync_to_async
    def process_pdf(self, filename):
        """Extracts text from a PDF and splits it into chunks."""
        elements = partition(filename=filename)
        full_text = "\n".join([element.text for element in elements])
        words = re.findall(r'\S+', full_text)  # Tokenize words
        chunks = []
        for i in range(0, len(words), CHUNK_SIZE - OVERLAP):
            chunk = " ".join(words[i:i + CHUNK_SIZE])
            chunks.append(chunk)
            # Stop if last chunk is reached
            if i + CHUNK_SIZE >= len(words):
                break
        return chunks

    async def store_in_weaviate(self, chunks, source, documentUUID) -> str:
        """Stores document chunks in Weaviate."""
        weaviate_client = weaviate.use_async_with_weaviate_cloud(cluster_url=WEAVIATE_HOST, auth_credentials=Auth.api_key(WEAVIATE_PASSWORD))
        await weaviate_client.connect()
        if not weaviate_client:
            raise ValueError("Weaviate client is not initialized!")
        if not weaviate_client.is_connected():
            raise ValueError("Weaviate client is not able to connect!")
        chunksVector = await self.aembedding(chunks=chunks)
        async with weaviate_client as client:
            data_objects = [
                wvc.data.DataObject(
                    properties={
                        "textChunk": chunk,
                        "chunkRank": i + 1,
                        "documentUUID": documentUUID
                    },
                    vector=chunksVector[i]
                )
                for i, chunk in enumerate(chunks)
            ]
            collection = client.collections.get("Document_db")
            await collection.data.insert_many(
                data_objects
            )
        await weaviate_client.close()
        return f"Successfully stored {len(chunks)} chunks in Weaviate!"
        

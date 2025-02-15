from langchain_community.embeddings import OllamaEmbeddings
from aisolution.settings import OLLAMA_URL


class ChunkEmbedding:

    async def aembedding(self, chunks: list[str]) -> list[list[float]]:
        try:
            ollamaEmbedding = OllamaEmbeddings(base_url=OLLAMA_URL, model="bge-large")
            print(ollamaEmbedding,"ollamaEmbedding")
            return await ollamaEmbedding.aembed_documents(texts=chunks)
        except Exception as e:
            raise Exception(e)

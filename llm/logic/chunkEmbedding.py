from langchain_community.embeddings import OllamaEmbeddings
from aisolution.settings import OLLAMA_URL, EMBEDDING_MODEL

ollamaEmbedding = OllamaEmbeddings(base_url=OLLAMA_URL, model=EMBEDDING_MODEL)


class ChunkEmbedding:

    async def aembed(self, question: str) -> list[list[float]]:
        try:
            return await ollamaEmbedding.aembed_query(text=question)
        except Exception as e:
            raise Exception(e)

    async def aembedding_batch(self, chunks: list[str]) -> list[list[float]]:
        try:

            return await ollamaEmbedding.aembed_documents(texts=chunks)
        except Exception as e:
            raise Exception(e)

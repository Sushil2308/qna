from aisolution.settings import OLLAMA_URL, LLM_INFERENCE_MODEL
from asgiref.sync import sync_to_async
from langchain_community.chat_models.ollama import ChatOllama


class CustomLLMInstance:

    @sync_to_async
    def getModel(self) -> ChatOllama:
        try:
            return ChatOllama(
                base_url=OLLAMA_URL,
                model=LLM_INFERENCE_MODEL,
                temperature=0,
                streaming=True,
            )
        except Exception as e:
            raise Exception(e)

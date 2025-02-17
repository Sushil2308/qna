from langchain.text_splitter import RecursiveCharacterTextSplitter
from asgiref.sync import sync_to_async
from aisolution.settings import CHUNK_SIZE, OVERLAP

class TextChunker:
    
    def __init__(self):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE,       
            chunk_overlap=OVERLAP,    
            length_function=len
        )

    @sync_to_async
    def getChunks(self, text):
        try:
            return self.text_splitter.split_text(text)
        except Exception as e:
            raise Exception(e)



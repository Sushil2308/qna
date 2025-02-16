import json
from urllib.parse import parse_qs
from channels.generic.websocket import AsyncWebsocketConsumer
from langchain.schema import HumanMessage, SystemMessage, AIMessage
from llm.logic import QNA_SYSTEM_PROMPT, CustomLLMInstance, ChunkEmbedding
import weaviate
from weaviate.classes.init import Auth
from aisolution.settings import WEAVIATE_HOST, WEAVIATE_PASSWORD, COLLECTION_DB
from uuid import UUID
from functools import reduce
from qna.models import SessionDocumentInfo
from qna.models import ChatSessionManager, SessionDocumentInfo, SessionChatInfo
from weaviate.classes.query import Filter
from io import StringIO


class QnaStreamConsumer(AsyncWebsocketConsumer, CustomLLMInstance, ChunkEmbedding):
    async def connect(self):
        try:
            """Accepts the WebSocket connection and extracts documentUUID from query parameters."""
            query_string = parse_qs(self.scope["query_string"].decode())
            self.session_uuid = query_string.get("sessionUUID", [None])[0]
            self.user = self.scope["user"]
            self.session = await ChatSessionManager.objects.aget(
                sessionUUID=self.session_uuid, user=self.user
            )
            if not self.session_uuid:
                await self.close(code=4001)
                return
            self.llm = await self.getModel()
            self.preChats = await self.getPreChats()
            self.weaviate_client = weaviate.use_async_with_weaviate_cloud(
                cluster_url=WEAVIATE_HOST,
                auth_credentials=Auth.api_key(WEAVIATE_PASSWORD),
                skip_init_checks=True,
            )
            # Fetch all documentUUIDs related to the session asynchronously
            self.documentUUIDs = await self.getIndexedDocuments()
            await self.accept()
            await self.send(json.dumps({"message": "Connected to WebSocket!"}))
        except ChatSessionManager as e:
            await self.send(json.dumps({"error": "Invalid Session"}))
        except Exception as e:
            await self.send(json.dumps({"error": "Invalid JSON format"}))

    async def getIndexedDocuments(self):
        try:
            return [
                document_uuid
                async for document_uuid in SessionDocumentInfo.objects.filter(
                    chatSession__sessionUUID=self.session_uuid,
                    chatSession__user=self.user,
                ).values_list("document__documentUUID", flat=True)
            ]
        except Exception as e:
            raise Exception(e)

    async def getPreChats(self):
        try:
            messages = []
            async for chatInfo in (
                SessionChatInfo.objects.filter(chatSession_id=self.session.pk)
                .values("userQuestion", "aiResponse")
                .order_by("-generatedOn")[:4]
            ):
                messages.extend(
                    [
                        HumanMessage(content=chatInfo["userQuestion"]),
                        AIMessage(content=chatInfo["aiResponse"]),
                    ]
                )
            return messages
        except Exception as e:
            raise Exception(e)

    async def fetchSimilarRecordsFromVectorDB(
        self, question: str, documentUUIDs: list[UUID]
    ) -> dict:
        try:
            # Step 3: Attempt to connect to Weaviate
            await self.weaviate_client.connect()
            filter_conditions = Filter.all_of(
                [  # OR condition for multiple filters
                    Filter.by_property("documentUUID").contains_any(documentUUIDs),
                ]
            )
            collection = self.weaviate_client.collections.get(COLLECTION_DB)
            vector = await self.aembed(question=question)
            results = await collection.query.hybrid(
                query=question,
                alpha=0.75,
                limit=5,
                filters=filter_conditions,
                return_properties=["textChunk"],
                vector=vector,
            )
            results = results.__dict__
            results = reduce(
                lambda acc, record: acc + record.properties["textChunk"],
                results["objects"],
                "",
            )
            return results
        except Exception as e:
            raise Exception(e)

    async def receive(self, text_data):
        """Handles incoming messages, extracts the question, and streams LangChain's response."""
        try:
            data = json.loads(text_data)  # Parse JSON data
            question = data.get("question", "")

            if not question:
                await self.send(json.dumps({"error": "No question provided"}))
                return

            documentContext = await self.fetchSimilarRecordsFromVectorDB(
                question=question, documentUUIDs=self.documentUUIDs
            )

            # Notify the client that streaming is start
            await self.send(json.dumps({"type": "status", "response": "Start"}))

            aiResponse = StringIO("")
            async for chunk in self.stream_response(
                question=question, documentContext=documentContext
            ):
                aiResponse.write(chunk)
                await self.send(json.dumps({"type": "answer", "response": chunk}))
            await SessionChatInfo.objects.acreate(
                **{
                    "chatSession_id": self.session.pk,
                    "userQuestion": question,
                    "aiResponse": aiResponse.getvalue(),
                }
            )
            # Notify the client that streaming is complete
            await self.send(json.dumps({"type": "status", "response": "end"}))
            if len(self.preChats) > 2:
                # Remove the Old One
                self.preChats = self.preChats[2:]
                # Insert New One
                self.preChats.extend(
                    [HumanMessage(content=question), AIMessage(content=aiResponse)]
                )

        except json.JSONDecodeError:
            await self.send(json.dumps({"error": "Invalid JSON format"}))

    async def stream_response(self, question, documentContext):
        try:
            """Calls Deepseek AI model and streams response chunk by chunk."""
            context = """\n**Document Context**\n{documentContext}\n**User Question**:\n{userQuery}""".format(
                documentContext=documentContext, userQuery=question
            )
            mergeMessages = (
                [SystemMessage(content=QNA_SYSTEM_PROMPT)]
                + self.preChats
                + [HumanMessage(content=context)]
            )
            async for chunk in self.llm.astream(mergeMessages):
                # Send chunk to WebSocket client
                yield chunk.content
        except Exception as e:
            raise Exception(e)

    async def disconnect(self, close_code):
        """Handles WebSocket disconnection."""
        print(f"WebSocket disconnected with code {close_code}")

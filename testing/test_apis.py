import aiohttp
import asyncio
import json
import sys

# Define API base URLs
ENDPOINT = "127.0.0.1:8000"
AUTH_BASE_URL = f"http://{ENDPOINT}/auth"
DOCUMENT_BASE_URL = f"http://{ENDPOINT}/docops/ingestion"
CHAT_BASE_URL = f"http://{ENDPOINT}/qna/session"
WEBSOCKET_URL = f"ws://{ENDPOINT}/qna/docChat"

USERNAME = "admin"
PASSWORD = "admin"
TOKEN = None


# Helper function to handle POST requests
async def post_request(session, url, data, headers=None):
    async with session.post(url, json=data, headers=headers) as response:
        return await response.json(), response.status


# Helper function to handle GET requests
async def get_request(session, url, params=None, headers=None):
    async with session.get(url, params=params, headers=headers) as response:
        return await response.json(), response.status


async def websocket_request(url, session_uuid, token):
    headers = {
        "Authorization": f"Token {token}",
    }
    async with aiohttp.ClientSession() as session:
        async with session.ws_connect(
            f"{url}?sessionUUID={session_uuid}", headers=headers
        ) as ws:
            print("Connected to WebSocket!")
            await ws.send_json({"question": "What is the summary of the document?"})
            async for msg in ws:
                if msg.type == aiohttp.WSMsgType.TEXT:
                    data = json.loads(msg.data)
                    if "type" in data:
                        sys.stdout.write(data["response"])
                        sys.stdout.flush()
                    if "type" in data and data["response"] == "end":
                        break


# Authentication - Login
async def login():
    async with aiohttp.ClientSession() as session:
        login_data = {"username": USERNAME, "password": PASSWORD}
        response_data, status = await post_request(
            session, f"{AUTH_BASE_URL}/login", login_data
        )
        if status == 200:
            print("Login successful, token:", response_data["token"])
            return response_data["token"]
        else:
            print("Login failed:", response_data["error"])
            return None


# Authentication - Logout
async def logout():
    async with aiohttp.ClientSession() as session:
        headers = {"Authorization": f"Token {TOKEN}"}
        response_data, status = await post_request(
            session, f"{AUTH_BASE_URL}/logout", {}, headers
        )
        if status == 200:
            print("Logout successful:", response_data["message"])
        else:
            print("Logout failed:", response_data)


# Document ingestion - POST
async def ingest_document():
    async with aiohttp.ClientSession() as session:
        ingest_data = {
            "name": "Sample Document",
            "text": "This is the content of the document.",
        }
        headers = {"Authorization": f"Token {TOKEN}"}
        response_data, status = await post_request(
            session, f"{DOCUMENT_BASE_URL}", ingest_data, headers
        )
        if status == 201:
            print("Document successfully ingested:", response_data["message"])
            return response_data["message"]["DocumentUUID"]
        else:
            print("Document ingestion failed:", response_data)


# Document retrieval - GET
async def get_documents():
    async with aiohttp.ClientSession() as session:
        params = {"perPage": 10, "page": 1}
        headers = {"Authorization": f"Token {TOKEN}"}
        response_data, status = await get_request(
            session, f"{DOCUMENT_BASE_URL}", params, headers
        )
        if status == 200:
            print("Documents retrieved successfully:", response_data)
        else:
            print("Failed to retrieve documents:", response_data)


# Chat session management - Create a session
async def create_chat_session():
    async with aiohttp.ClientSession() as session:
        response_data, status = await post_request(
            session, f"{CHAT_BASE_URL}", {}, {"Authorization": f"Token {TOKEN}"}
        )
        if status == 201:
            print("Chat session created successfully:", response_data["sessionUUID"])
            return response_data["sessionUUID"]
        else:
            print("Failed to create chat session:", response_data)


# Add documents to a session
async def add_documents_to_session(session_uuid, document_uuids):
    async with aiohttp.ClientSession() as session:
        add_data = {"sessionUUID": session_uuid, "documentUUIDs": document_uuids}
        response_data, status = await post_request(
            session, f"{CHAT_BASE_URL}", add_data, {"Authorization": f"Token {TOKEN}"}
        )
        if status == 200:
            print("Documents added to session successfully:", response_data)
        else:
            print("Failed to add documents:", response_data)


# Main testing function
async def test_api():
    global TOKEN

    # Step 1: Authenticate (Login)
    TOKEN = await login()
    if not TOKEN:
        return

    # Step 2: Ingest a document
    document_uuid = await ingest_document()

    # Step 3: Retrieve documents
    await get_documents()

    # Step 4: Create a chat session
    session_uuid = await create_chat_session()

    # Step 5: Add documents to chat session
    await add_documents_to_session(session_uuid, [document_uuid])

    # Step 6: Test WebSocket connection
    await websocket_request(WEBSOCKET_URL, session_uuid, token=TOKEN)

    # Step 7: Logout
    await logout()


# Run the test
if __name__ == "__main__":
    asyncio.run(test_api())

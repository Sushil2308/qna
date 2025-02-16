import json
from channels.middleware import BaseMiddleware
from rest_framework.authtoken.models import Token
from asgiref.sync import sync_to_async

class AsyncAuthMiddleware(BaseMiddleware):
    async def __call__(self, scope, receive, send):
        """Middleware for authenticating WebSocket requests using Django Token Authentication."""
        
        headers = dict(scope["headers"])
        auth_header = headers.get(b"authorization", b"").decode()

        if not auth_header.startswith("Token "):
            await self.send_error_response(send, {"error": "Authentication failed"}, status=401)
        token_key = auth_header.split(" ")[1]
        try:
            token_obj = await Token.objects.aget(key=token_key)
            scope["user"] = await sync_to_async(lambda: token_obj.user)()
            # Continue processing if authentication is successful
            await super().__call__(scope, receive, send)
        except Token.DoesNotExist:
            await self.send_error_response(send, {"error": "Invalid token"}, status=401)
            return
        except Exception as e:
            print(str(e))
            await self.send_error_response(send, {"error": "Authentication failed"}, status=401)
            return
        
        

    async def send_error_response(self, send, message, status):
        """Send an error response and close the WebSocket connection."""
        await send({
            "type": "websocket.close",
            "code": status 
        })
        await send({
            "type": "websocket.send",
            "text": json.dumps(message)
        })



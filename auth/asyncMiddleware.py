import asyncio
from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token

class AsyncJWTAuthenticationMiddleware(MiddlewareMixin):
    def __init__(self, get_response):
        self.get_response = get_response

    async def __call__(self, request):
        """Handles JWT authentication for ASGI apps (Daphne support)."""
        print("Here",request.path,"kkkk")
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Token "):
            token = auth_header.split(" ")[1]
            try:
                # Fetch user asynchronously to avoid blocking in ASGI
                user = await Token.objects.get(id=token).user
                # Attach user to request
                request.user = user

            except User.DoesNotExist:
                return JsonResponse({"error": "Invalid token"}, status=401)
            except Exception:
                return JsonResponse({"error": "Authentication failed"}, status=401)

        else:
            return JsonResponse({"error": "Authentication required"}, status=401)

        return await self._get_response(request)

    async def _get_response(self, request):
        """Handles both async and sync views."""
        if asyncio.iscoroutinefunction(self.get_response):
            return await self.get_response(request)  # Async View
        return self.get_response(request)  # Sync View

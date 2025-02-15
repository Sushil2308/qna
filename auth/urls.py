from django.urls import path
from .views import CustomLoginView, LogoutView

urlpatterns = [
    path('api/login/', CustomLoginView.as_view(), name='custom_login'),
    path('api/logout/', LogoutView.as_view(), name='logout'),
]

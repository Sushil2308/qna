from django.urls import path
from .views import CustomLoginView, LogoutView

urlpatterns = [
    path('login', CustomLoginView.as_view(), name='custom_login'),
    path('logout', LogoutView.as_view(), name='logout'),
]

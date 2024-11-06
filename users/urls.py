from django.urls import path
from .views import LoginView, UserRegistrationView
from rest_framework_simplejwt.views import TokenObtainPairView

urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='token_obtain_pair'),
     path('users/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
]

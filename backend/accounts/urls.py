from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import RegisterView, ProfileView, ProfileEditView

urlpatterns = [
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('register/', RegisterView.as_view(), name='register'),
    path('profile/edit/', ProfileEditView.as_view(), name='edit'),
    path('profile/view/', ProfileView.as_view(), name='detail'),
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
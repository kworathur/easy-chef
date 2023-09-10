from django.urls import path
from .views import RegisterView, ProfileView, ProfileEditView, CookieTokenRefreshView, CookieTokenObtainPairView

urlpatterns = [
    path('auth/token/', CookieTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', CookieTokenRefreshView.as_view(), name='token_refresh'),
    path('register/', RegisterView.as_view(), name='register'),
    path('profile/edit/', ProfileEditView.as_view(), name='edit'),
    path('profile/view/', ProfileView.as_view(), name='detail')
]
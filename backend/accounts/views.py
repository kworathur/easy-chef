from rest_framework.generics import CreateAPIView, UpdateAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from .serializers import CreateUserSerializer, UserSerializer

# Create your views here.
class RegisterView(CreateAPIView):

    serializer_class = CreateUserSerializer

class ProfileView(RetrieveAPIView):

    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

class ProfileEditView(UpdateAPIView):

    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

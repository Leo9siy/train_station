from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.generics import CreateAPIView, RetrieveUpdateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.settings import api_settings

from user.serializers import UserSerializer, AuthTokenSerializer


class UserCreateApi(CreateAPIView):
    serializer_class = UserSerializer
    permission_classes = [AllowAny]


class UserLoginApi(ObtainAuthToken):
    serializer_class = AuthTokenSerializer
    permission_classes = [AllowAny]
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES


class UserRetrieveUpdateAPIView(RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

from rest_framework import generics, status, permissions
from rest_framework.response import Response
from users.models import User
from users.api.serializers import RegisterSerializer, UserSerializer


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (permissions.AllowAny,)
    serializer_class = RegisterSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # User is created but not active until email is verified
        if user.role != "admin":
            user.is_active = False
            user.save()
            message = "User registered successfully. Please verify your email."
        else:
            message = "Admin user registered successfully."

        return Response({
            'message': message,
            # 'user': UserSerializer(user).data
        }, status=status.HTTP_201_CREATED)
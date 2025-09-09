from rest_framework import generics, permissions
from users.api.serializers import UserSerializer
from rest_framework.response import Response
from rest_framework import status


class UserProfileView(generics.RetrieveAPIView):
    serializer_class = UserSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self):
        return self.request.user


class UserProfileUpdateView(generics.UpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response(
            {
                "success": True,
                "message": "Profile updated successfully",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )
    

class UserProfileDeleteView(generics.DestroyAPIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self):
        return self.request.user

    def delete(self, request, *args, **kwargs):
        user = self.get_object()
        user.delete()
        return Response(
            {
                "success": True,
                "message": "User profile deleted successfully"
            },
            status=status.HTTP_200_OK,
        )

from rest_framework import generics, status, permissions
from rest_framework.response import Response

from django.contrib.auth import update_session_auth_hash

from users.api.serializers import (
    ChangePasswordSerializer,
)


class ChangePasswordView(generics.GenericAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = ChangePasswordSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = request.user
        old_password = serializer.validated_data['old_password']
        new_password = serializer.validated_data['new_password']

        if not user.check_password(old_password):
            return Response(
                {'error': 'Current password is incorrect'},
                status=status.HTTP_400_BAD_REQUEST
            )

        user.set_password(new_password)
        user.save()

        # Update session auth hash to keep user logged in
        update_session_auth_hash(request, user)

        return Response({'message': 'Password changed successfully'})
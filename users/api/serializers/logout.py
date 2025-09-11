from rest_framework import serializers


class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()
    
    def validate(self, attrs):
        self.refresh_token = attrs['refresh']
        return attrs
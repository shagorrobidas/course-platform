from rest_framework import serializers
from django.contrib.auth import authenticate


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    
    def validate(self, data):
        email = data.get('email')
        password = data.get('password')
        
        if email and password:
            user = authenticate(
                request=self.context.get('request'),
                email=email, password=password
            )
            if not user:
                raise serializers.ValidationError('Invalid credentials')
            if not user.is_email_verified:
                raise serializers.ValidationError('Email not verified')
        else:
            raise serializers.ValidationError(
                'Must include "email" and "password"'
            )
        
        data['user'] = user
        return data
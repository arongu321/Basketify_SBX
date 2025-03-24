from django.conf import settings
from rest_framework import serializers
from .models import UserFavorite

User = settings.AUTH_USER_MODEL

# written by zach
class UserFavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserFavorite
        fields = ['favorite_type', 'favorite_name']

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'email_is_verified']
        read_only_fields = ['id', 'email_is_verified']

class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    email = serializers.EmailField(required=True)
    
    class Meta:
        model = User
        fields = ['id', 'email', 'password']
        read_only_fields = ['id']
    
    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
        )
        return user
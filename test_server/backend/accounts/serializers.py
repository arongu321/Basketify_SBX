from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import UserFavorite

# Fulfills FR5 and FR6 by modelling PostgreSQL user favourite fields to Python objects
class UserFavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserFavorite
        fields = ['favorite_type', 'favorite_name']


# written by Aron
User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    favorites = UserFavoriteSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = ['id', 'email', 'email_is_verified', 'favorites']
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
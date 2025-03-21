from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth.models import User
from .serializers import UserSerializer, UserCreateSerializer, UserFavoriteSerializer
from .models import UserFavorite

class UserRegistrationView(generics.CreateAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = UserCreateSerializer

class UserDetailView(generics.RetrieveUpdateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserSerializer
    
    def get_object(self):
        return self.request.user

class SetFavoriteView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        user = request.user
        favorite_type = request.data.get('type')
        favorite_name = request.data.get('name')

        if favorite_type not in ['player', 'team']:
            return Response({"error": "Invalid favorite type"}, status=status.HTTP_400_BAD_REQUEST)
        if not favorite_name:
            return Response({"error": "Favorite name is required"}, status=status.HTTP_400_BAD_REQUEST)

        # update or create favourite
        UserFavorite.objects.update_or_create(
            user=user,
            favorite_type=favorite_type,
            defaults={'favorite_name': favorite_name}
        )
        return Response({"message": f"Favorite {favorite_type} set to {favorite_name}"}, status=status.HTTP_200_OK)
    

# written by Zach
class GetFavoriteView(APIView):
    permission_classes = [permissions.IsAuthenticated]  # user must be logged in to get their favourites

    def get(self, request):
        user = request.user
        favorites = UserFavorite.objects.filter(user=user)  # get player & team faves (one player and one team)

        if not favorites.exists():
            return Response({'message': 'No favorites set'}, status=status.HTTP_404_NOT_FOUND)

        favorite_data = {'player': None, 'team': None}
        
        for favorite in favorites:
            if favorite.favorite_type == 'player':
                favorite_data['player'] = favorite.favorite_name
            elif favorite.favorite_type == 'team':
                favorite_data['team'] = favorite.favorite_name

        return Response(favorite_data, status=status.HTTP_200_OK)


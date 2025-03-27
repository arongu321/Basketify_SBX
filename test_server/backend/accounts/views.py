from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.views import APIView
from django.contrib.auth.models import User
from .serializers import UserSerializer, UserCreateSerializer
from .models import UserFavorite
from django.shortcuts import redirect, render
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from .tokens import account_activation_token
from django.core.mail import EmailMessage
from django.contrib import messages
from django.contrib.auth import get_user_model
from datetime import datetime
import json

User = get_user_model()

class UserRegistrationView(generics.CreateAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = UserCreateSerializer

    def perform_create(self, serializer):
        user = serializer.save()
        # Automatically send verification email
        current_site = get_current_site(self.request)
        subject = "Verify Your Email"
        # Update to use the new HTML email template
        current_year = datetime.now().year
        
        # Build verification URL for frontend
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = account_activation_token.make_token(user)
        
        # Get frontend URL - use a default if not available
        frontend_url = self.request.META.get('HTTP_REFERER', 'http://localhost:3000')
        # Extract base URL from referrer or use default
        if frontend_url.endswith('/'):
            frontend_url = frontend_url[:-1]
            
        # If we can extract the base URL from referrer, do so, otherwise use default
        try:
            base_url = frontend_url.split('/')[0] + '//' + frontend_url.split('/')[2]
        except (IndexError, AttributeError):
            base_url = 'http://localhost:3000'
            
        verification_url = f"{base_url}/verify-email-confirm/{uid}/{token}"
        
        # Use the HTML template
        message = render_to_string('accounts/verify_email_message.html', {
            'verification_url': verification_url,
            'current_year': current_year
        })
        
        to_email = user.email
        email = EmailMessage(
            subject, message, to=[to_email]
        )
        email.content_subtype = 'html'
        email.send()

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

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def verify_email(request):
    """API endpoint to request a verification email"""
    if request.user.email_is_verified != True:
        current_site = get_current_site(request)
        user = request.user
        email_address = request.user.email
        subject = "Verify Email"
        
        # Build verification URL for frontend
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = account_activation_token.make_token(user)
        frontend_url = request.META.get('HTTP_REFERER', 'http://localhost:3000')
        # Extract base URL from referrer or use default
        if frontend_url.endswith('/'):
            frontend_url = frontend_url[:-1]
        base_url = frontend_url.split('/')[0] + '//' + frontend_url.split('/')[2]
        verification_url = f"{base_url}/verify-email-confirm/{uid}/{token}"
        current_year = datetime.now().year
        
        # Use the HTML template
        message = render_to_string('accounts/verify_email_message.html', {
            'verification_url': verification_url,
            'current_year': current_year
        })
        
        email = EmailMessage(
            subject, message, to=[email_address]
        )
        email.content_subtype = 'html'
        email.send()
        
        return Response({
            'status': 'success',
            'message': 'Verification email sent successfully'
        }, status=status.HTTP_200_OK)
    else:
        return Response({
            'status': 'error',
            'message': 'Email already verified'
        }, status=status.HTTP_400_BAD_REQUEST)

def verify_email_done(request):
    """Legacy Django view - this will be handled by React frontend"""
    return render(request, 'accounts/verify_email_done.html')

@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def verify_email_confirm(request, uidb64, token):
    """API endpoint to confirm email verification"""
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
        
    if user is not None and account_activation_token.check_token(user, token):
        user.email_is_verified = True
        user.save()
        
        return Response({
            'status': 'success',
            'message': 'Email verified successfully',
        }, status=status.HTTP_200_OK)
    else:
        return Response({
            'status': 'error',
            'message': 'Invalid verification link',
        }, status=status.HTTP_400_BAD_REQUEST)

def verify_email_complete(request):
    """Legacy Django view - this will be handled by React frontend"""
    return render(request, 'accounts/verify_email_complete.html')

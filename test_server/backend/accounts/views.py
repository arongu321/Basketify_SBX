from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
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
from datetime import datetime, timezone
from django.contrib.auth.tokens import default_token_generator
from django.db import IntegrityError
import json

# Import the custom user model
User = get_user_model()

class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Custom token view that checks for email verification and returns
    appropriate error messages.

    FR2 - This class implements user login by validating credentials and checking if email is verified
    """
    def post(self, request, *args, **kwargs):
        # FR2 - Check if email is verified before allowing login
        try:
            # Get the email from the request
            email = request.data.get('email', '')
            
            # Check if the user exists and if email is verified
            try:
                user = User.objects.get(email=email)
                if not user.email_is_verified:
                    # FR2 - Return appropriate error for unverified email
                    return Response(
                        {
                            "detail": "Email not verified. Please check your inbox for the verification email.",
                            "code": "email_not_verified"
                        },
                        status=status.HTTP_401_UNAUTHORIZED
                    )
            except User.DoesNotExist:
                # Don't reveal that the user doesn't exist, proceed with normal flow
                pass
                
            # Call the parent class method to handle the token creation
            # FR2 - Generate JWT token for authenticated users
            return super().post(request, *args, **kwargs)
        except Exception as e:
            # This will catch any other authentication errors
            return Response(
                {"detail": str(e)},
                status=status.HTTP_401_UNAUTHORIZED
            )

class UserRegistrationView(generics.CreateAPIView):
    """
    # FR1 - Handles user registration by creating new user accounts with email and password
    """
    permission_classes = [permissions.AllowAny]
    serializer_class = UserCreateSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        
        # Check if the email already exists
        email = request.data.get('email', '')
        if self.get_user_model().objects.filter(email=email).exists():
            return Response(
                {"email": ["A user with this email already exists."]},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Continue with normal validation
        if serializer.is_valid():
            try:
                self.perform_create(serializer)
                headers = self.get_success_headers(serializer.data)
                return Response(
                    serializer.data, 
                    status=status.HTTP_201_CREATED, 
                    headers=headers
                )
            except IntegrityError:
                # Catch any IntegrityError that might still occur
                return Response(
                    {"email": ["A user with this email already exists."]},
                    status=status.HTTP_400_BAD_REQUEST
                )
        else:
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
    
    def get_user_model(self):
        return get_user_model()

    def perform_create(self, serializer):
        # FR1 - Send verification email after user creation
        user = serializer.save()
        # Automatically send verification email
        current_site = get_current_site(self.request)
        subject = "Verify Your Email"
        # Update to use the new HTML email template
        current_year = datetime.now().year
        
        # Build verification URL for frontend
        # FR1 - Create unique token for email verification
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
@permission_classes([permissions.AllowAny])
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

# Update the verify_email_confirm view in accounts/views.py to handle the token properly
# and provide more descriptive error messages

@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def verify_email_confirm(request, uidb64, token):
    """API endpoint to confirm email verification"""
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
        return Response({
            "status": "error",
            "message": "Invalid user identifier",
        }, status=status.HTTP_400_BAD_REQUEST)
        
    # Check if the user exists and token is valid
    if user is not None and account_activation_token.check_token(user, token):
        # Mark email as verified
        user.email_is_verified = True
        user.save()
        
        return Response({
            "status": "success",
            "message": "Email verified successfully",
        }, status=status.HTTP_200_OK)
    else:
        # Return detailed error for debugging
        if user is None:
            error_message = "User not found"
        else:
            error_message = "Invalid token"
            
        return Response({
            "status": "error",
            "message": f"Invalid verification link: {error_message}",
        }, status=status.HTTP_400_BAD_REQUEST)

def verify_email_complete(request):
    """Legacy Django view - this will be handled by React frontend"""
    return render(request, 'accounts/verify_email_complete.html')

# FR3 - Password reset request implementation
@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def password_reset_request(request):
    """
    API endpoint to initiate password reset process

    FR3 - Handles password reset requests by sending email with reset token
    """
    email = request.data.get('email', '')
    
    if not email:
        return Response({"error": "Email is required"}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        user = User.objects.get(email=email)
        
        # Generate token and uid
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        
        # Build reset URL for frontend
        current_site = get_current_site(request)
        frontend_url = request.META.get('HTTP_REFERER', 'http://localhost:3000')
        
        # Extract base URL from referrer or use default
        if frontend_url.endswith('/'):
            frontend_url = frontend_url[:-1]
        
        try:
            base_url = frontend_url.split('/')[0] + '//' + frontend_url.split('/')[2]
        except (IndexError, AttributeError):
            base_url = 'http://localhost:3000'
        
        reset_url = f"{base_url}/password-reset-confirm/{uid}/{token}"
        
        # Prepare email
        subject = "Reset Your Password"
        current_year = datetime.now().year
        
        # Use HTML email template
        html_message = render_to_string('accounts/password_reset_email.html', {
            'reset_url': reset_url,
            'current_year': current_year,
            'user': user,
        })
        
        # Send email
        email_message = EmailMessage(
            subject, html_message, to=[user.email]
        )
        email_message.content_subtype = 'html'
        email_message.send()
        
        return Response({
            "status": "success",
            "message": "Password reset email has been sent."
        }, status=status.HTTP_200_OK)
        
    except User.DoesNotExist:
        # For security reasons, don't reveal if email exists or not
        return Response({
            "status": "success",
            "message": "If your email exists in our database, you will receive a password reset link."
        }, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def password_reset_done(request):
    """Return a success message when password reset email is sent"""
    return Response({
        "status": "success",
        "message": "Password reset email has been sent."
    })

@api_view(['GET', 'POST'])
@permission_classes([permissions.AllowAny])
def password_reset_confirm(request, uidb64, token):
    """Verify the reset token and allow password reset"""
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    
    # For GET requests, validate token
    if request.method == 'GET':
        if user is not None and default_token_generator.check_token(user, token):
            return Response({
                "status": "success",
                "message": "Token is valid",
                "uidb64": uidb64,
                "token": token
            })
        else:
            return Response({
                "status": "error",
                "message": "Invalid reset link"
            }, status=status.HTTP_400_BAD_REQUEST)
    
    # For POST requests, set new password
    elif request.method == 'POST':
        if user is not None and default_token_generator.check_token(user, token):
            password = request.data.get('password')
            
            if not password:
                return Response({
                    "status": "error",
                    "message": "Password is required"
                }, status=status.HTTP_400_BAD_REQUEST)
            
            user.set_password(password)
            user.save()
            
            return Response({
                "status": "success",
                "message": "Password has been reset successfully"
            })
        else:
            return Response({
                "status": "error",
                "message": "Invalid reset link"
            }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def password_reset_complete(request):
    """Return a success message when password reset is complete"""
    return Response({
        "status": "success",
        "message": "Password has been reset successfully"
    })

# FR3 - Email change request implementation
@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def email_change_request(request):
    """
    API endpoint to initiate email change process
    
    FR3 - Handles email change requests by sending email with verification token"""
    email = request.data.get('email', '')
    
    if not email:
        return Response({"error": "Email is required"}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        user = User.objects.get(email=email)
        
        # Update verification token timestamp and generate token and uid
        user.update_verification_token_timestamp()
        token = account_activation_token.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        
        # Build verification URL for frontend
        current_site = get_current_site(request)
        frontend_url = request.META.get('HTTP_REFERER', 'http://localhost:3000')
        
        # Extract base URL from referrer or use default
        if frontend_url.endswith('/'):
            frontend_url = frontend_url[:-1]
        
        try:
            base_url = frontend_url.split('/')[0] + '//' + frontend_url.split('/')[2]
        except (IndexError, AttributeError):
            base_url = 'http://localhost:3000'
        
        verification_url = f"{base_url}/email-reset-confirm/{uid}/{token}"
        
        # Prepare email
        subject = "Change Your Email"
        current_year = datetime.now().year
        
        # Use HTML email template
        html_message = render_to_string('accounts/email_change_email.html', {
            'verification_url': verification_url,
            'current_year': current_year,
            'user': user,
            'expiry_time': '2 minutes'
        })
        
        # Send email
        email_message = EmailMessage(
            subject, html_message, to=[user.email]
        )
        email_message.content_subtype = 'html'
        email_message.send()
        
        return Response({
            "status": "success",
            "message": "Email verification has been sent."
        }, status=status.HTTP_200_OK)
        
    except User.DoesNotExist:
        return Response({
            "status": "error",
            "message": "No account exists with this email address."
        }, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def email_change_confirm(request, uidb64, token):
    """API endpoint to confirm email change request"""
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    
    # Check if token is valid and not expired
    if user is not None and account_activation_token.check_token(user, token):
        # Check if token is within the 2-minute window
        if user.is_verification_token_expired():
            return Response({
                "status": "error",
                "message": "Verification link has expired. Please request a new one.",
                "expired": True
            }, status=status.HTTP_400_BAD_REQUEST)
            
        return Response({
            "status": "success",
            "message": "Verification successful. You can now change your email.",
            "uid": uidb64,
            "token": token
        })
    else:
        return Response({
            "status": "error",
            "message": "Invalid verification link",
        }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def email_change_complete(request, uidb64, token):
    """Complete the email change process"""
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    
    new_email = request.data.get('new_email', '')
    
    if not new_email:
        return Response({
            "status": "error",
            "message": "New email is required"
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Check if token is valid
    if user is not None and account_activation_token.check_token(user, token):
        # Check if token is within the 2-minute window
        if user.is_verification_token_expired():
            return Response({
                "status": "error",
                "message": "Verification link has expired. Please request a new one.",
                "expired": True
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if the new email is different from the current one
        if user.email == new_email:
            return Response({
                "status": "error",
                "message": "New email must be different from your current email"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if the new email is already in use
        if User.objects.filter(email=new_email).exists():
            return Response({
                "status": "error",
                "message": "This email is already registered with another account"
            }, status=status.HTTP_400_BAD_REQUEST)
            
        # Update the email
        old_email = user.email
        user.email = new_email
        user.email_is_verified = False  # Require verification of new email
        user.update_verification_token_timestamp()  # Update the verification token timestamp
        
        # Send confirmation email to both old and new email addresses
        subject = "Email Changed Successfully"
        current_year = datetime.now().year
        
        # Email to old address
        old_email_message = render_to_string('accounts/email_change_success_old.html', {
            'user': user,
            'old_email': old_email,
            'new_email': new_email,
            'current_year': current_year
        })
        
        email = EmailMessage(
            subject, old_email_message, to=[old_email]
        )
        email.content_subtype = 'html'
        email.send()
        
        user.save()

        # Create a fresh token based on the updated user data
        token = account_activation_token.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))

        # Build verification URL for frontend
        frontend_url = request.META.get('HTTP_REFERER', 'http://localhost:3000')
        if frontend_url.endswith('/'):
            frontend_url = frontend_url[:-1]

        try:
            base_url = frontend_url.split('/')[0] + '//' + frontend_url.split('/')[2]
        except (IndexError, AttributeError):
            base_url = 'http://localhost:3000'
            
        verification_url = f"{base_url}/verify-email-confirm/{uid}/{token}"

        # Add debug logging (optional)
        print(f"Generated verification URL: {verification_url}")
        
        new_email_message = render_to_string('accounts/email_change_verify_new.html', {
            'user': user,
            'verification_url': verification_url,
            'current_year': current_year,
            'old_email': old_email,
            'new_email': new_email
        })
        
        email = EmailMessage(
            "Verify Your New Email", new_email_message, to=[new_email]
        )
        email.content_subtype = 'html'
        email.send()
        
        return Response({
            "status": "success",
            "message": "Email updated successfully. Please verify your new email address."
        })
    else:
        return Response({
            "status": "error",
            "message": "Invalid verification link"
        }, status=status.HTTP_400_BAD_REQUEST)
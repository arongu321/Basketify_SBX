# Create a custom authentication backend that checks for email verification
# Create this in accounts/backends.py

from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend

User = get_user_model()

class EmailVerifiedBackend(ModelBackend):
    """
    Custom authentication backend that requires email verification.
    """
    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None:
            username = kwargs.get('email')
        if username is None or password is None:
            return None
        
        try:
            # Use the default manager rather than a custom manager here
            user = User.objects.get(email=username)
        except User.DoesNotExist:
            # Run the default password hasher to mitigate timing attacks
            User().check_password(password)
            return None
        
        if user.check_password(password) and self.user_can_authenticate(user):
            # Additional check for email verification
            if not user.email_is_verified:
                return None
            return user

    def user_can_authenticate(self, user):
        """
        Check if user is active and email is verified.
        """
        is_active = getattr(user, 'is_active', False)
        is_verified = getattr(user, 'email_is_verified', False)
        return is_active and is_verified
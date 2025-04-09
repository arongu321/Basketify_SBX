from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.base_user import BaseUserManager
from django.utils import timezone
from django.db import models
from django.conf import settings

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError(_('Email must be set'))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user
    
    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))
        return self.create_user(email, password, **extra_fields)

# Fulfills FR1 and FR2 by facilitating user login and registration with a custom user model with email and password
class CustomUser(AbstractUser):
    username = None
    email = models.EmailField(_("Email Address"), unique=True)
    email_is_verified = models.BooleanField(_("Email is Verified"), default=False)

    # Add timestamp for verification token creation
    verification_token_created = models.DateTimeField(_("Verification Token Created"), null=True, blank=True)
    
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []
    
    objects = CustomUserManager()
    
    def __str__(self):
        return self.email
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        
    def is_verification_token_expired(self):
        """Check if the verification token has expired (older than 2 minutes)"""
        if not self.verification_token_created:
            return True
            
        expiration_time = self.verification_token_created + timezone.timedelta(minutes=2)
        return timezone.now() > expiration_time
    
    def update_verification_token_timestamp(self):
        """Update the verification token creation timestamp to the current time"""
        self.verification_token_created = timezone.now()
        self.save(update_fields=['verification_token_created'])
    

# Fulfills FR5 and FR6 by modelling PostgreSQL user account favourite fields to Python objects
class UserFavorite(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='favorites')
    favorite_type = models.CharField(max_length=10, choices=[('player', 'Player'), ('team', 'Team')])
    favorite_name = models.CharField(max_length=100)
    
    class Meta:
        unique_together = ('user', 'favorite_type')  # ensures one fave team and one fave player per user in DB
    
    def __str__(self):
        return f"{self.user.email} favorite {self.favorite_type}: {self.favorite_name}"

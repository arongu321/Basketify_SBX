from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from accounts.models import CustomUser, UserFavorite
from unittest.mock import patch, MagicMock
from django.utils import timezone
import json
from datetime import timedelta

User = get_user_model()

class AuthenticationTestCase(TestCase):
    """Tests for user registration, login, and email/password change (FR1-FR3)"""
    
    def setUp(self):
        # Create a verified test user
        self.client = Client()
        self.verified_user = User.objects.create_user(
            email='verified@example.com',
            password='testpassword123',
            email_is_verified=True
        )
        # Create an unverified test user
        self.unverified_user = User.objects.create_user(
            email='unverified@example.com',
            password='testpassword123',
            email_is_verified=False
        )
        # URLs
        self.register_url = '/api/register/'
        self.login_url = '/api/token/'
        self.email_change_url = '/accounts/email-change/'
        self.password_reset_url = '/accounts/password-reset/'
        
    # FR1 - User Registration Tests
    def test_register_user_success(self):
        """Test successful user registration with valid data"""
        payload = {
            'email': 'newuser@example.com',
            'password': 'NewPassword123!'
        }
        response = self.client.post(self.register_url, payload, content_type='application/json')
        self.assertEqual(response.status_code, 201)
        self.assertTrue(User.objects.filter(email='newuser@example.com').exists())
        
    def test_register_existing_email(self):
        """Test registration with an email that already exists"""
        payload = {
            'email': 'verified@example.com',  # Email already in use
            'password': 'NewPassword123!'
        }
        response = self.client.post(self.register_url, payload, content_type='application/json')
        self.assertEqual(response.status_code, 400)
        
    def test_register_invalid_email(self):
        """Test registration with an invalid email format"""
        payload = {
            'email': 'not-an-email',
            'password': 'NewPassword123!'
        }
        response = self.client.post(self.register_url, payload, content_type='application/json')
        self.assertEqual(response.status_code, 400)
    
    # FR2 - User Login Tests
    def test_login_verified_user_success(self):
        """Test successful login for verified user"""
        payload = {
            'email': 'verified@example.com',
            'password': 'testpassword123'
        }
        response = self.client.post(self.login_url, payload, content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        
    def test_login_unverified_user(self):
        """Test login attempt with unverified email"""
        payload = {
            'email': 'unverified@example.com',
            'password': 'testpassword123'
        }
        response = self.client.post(self.login_url, payload, content_type='application/json')
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.data['code'], 'email_not_verified')
        
    def test_login_wrong_password(self):
        """Test login attempt with incorrect password"""
        payload = {
            'email': 'verified@example.com',
            'password': 'wrongpassword'
        }
        response = self.client.post(self.login_url, payload, content_type='application/json')
        self.assertEqual(response.status_code, 401)
        
    def test_login_nonexistent_user(self):
        """Test login attempt with email not in system"""
        payload = {
            'email': 'nonexistent@example.com',
            'password': 'testpassword123'
        }
        response = self.client.post(self.login_url, payload, content_type='application/json')
        self.assertEqual(response.status_code, 401)
    
    # FR3 - Email/Password Change Tests
    @patch('accounts.views.EmailMessage.send')
    def test_email_change_request_success(self, mock_send):
        """Test successful email change request"""
        mock_send.return_value = None  # Mock email sending
        
        # Login first to get token
        login_payload = {
            'email': 'verified@example.com',
            'password': 'testpassword123'
        }
        login_response = self.client.post(self.login_url, login_payload, content_type='application/json')
        token = login_response.data['access']
        
        # Request email change
        payload = {'email': 'verified@example.com'}
        response = self.client.post(
            self.email_change_url, 
            payload, 
            content_type='application/json',
            HTTP_AUTHORIZATION=f'Bearer {token}'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['status'], 'success')
        mock_send.assert_called_once()  # Email was sent
    
    @patch('accounts.views.EmailMessage.send')
    def test_password_reset_request_success(self, mock_send):
        """Test successful password reset request"""
        mock_send.return_value = None  # Mock email sending
        
        payload = {'email': 'verified@example.com'}
        response = self.client.post(self.password_reset_url, payload, content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['status'], 'success')
        mock_send.assert_called_once()  # Email was sent
    
    def test_password_reset_nonexistent_email(self):
        """Test password reset with email not in system"""
        payload = {'email': 'nonexistent@example.com'}
        response = self.client.post(self.password_reset_url, payload, content_type='application/json')
        # Should still return 200 for security reasons to not leak which emails exist
        self.assertEqual(response.status_code, 200)
        
    # Token expiration test
    def test_verification_token_expiration(self):
        """Test that verification tokens expire after 2 minutes"""
        # Set token creation time to 3 minutes ago
        self.unverified_user.verification_token_created = timezone.now() - timedelta(minutes=3)
        self.unverified_user.save()
        
        # Check if token is expired
        self.assertTrue(self.unverified_user.is_verification_token_expired())
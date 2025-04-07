from django.contrib.auth.tokens import PasswordResetTokenGenerator
from six import text_type

class TokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        # Include email_is_verified status in the token hash
        # This ensures a new token is generated after email_is_verified changes
        return (
            text_type(user.pk) + 
            text_type(timestamp) +
            text_type(user.email_is_verified) +
            text_type(user.email)  # Include email to make tokens unique after email change
        )

account_activation_token = TokenGenerator()
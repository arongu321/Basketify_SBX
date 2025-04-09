from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('register/', views.UserRegistrationView.as_view(), name='register'),
    path('profile/', views.UserDetailView.as_view(), name='profile'),

    # Set favorite URLs (FR5, FR6)
    path('set-favorite/', views.SetFavoriteView.as_view(), name='set_favorite'),
    path('get-favorite/', views.GetFavoriteView.as_view(), name='get_favorite'),

    # Verify email URLs (FR1)
    path('verify-email/', views.verify_email, name='verify-email'),
    path('verify-email/done/', views.verify_email_done, name='verify-email-done'),
    path('verify-email-confirm/<uidb64>/<token>/', views.verify_email_confirm, name='verify-email-confirm'),
    path('verify-email/complete/', views.verify_email_complete, name='verify-email-complete'),
    
    # Password reset URLs (FR3)
    path('password-reset/', views.password_reset_request, name='password_reset'),
    path('password-reset/done/', views.password_reset_done, name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/', views.password_reset_confirm, name='password_reset_confirm'),
    path('password-reset-complete/', views.password_reset_complete, name='password_reset_complete'),

    # Email change URLs (FR3)
    path('email-change/', views.email_change_request, name='email_change'),
    path('email-change-confirm/<uidb64>/<token>/', views.email_change_confirm, name='email_change_confirm'),
    path('email-change-complete/<uidb64>/<token>/', views.email_change_complete, name='email_change_complete'),

]
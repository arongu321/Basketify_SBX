from django.urls import path
from .views import welcome
from .views import get_login_message
from .views import get_search_message

urlpatterns = [
    path('', welcome, name='welcome'),
    path('login-message/', get_login_message, name='login_message'),
    path('search-message/', get_search_message, name='search_message'),
]

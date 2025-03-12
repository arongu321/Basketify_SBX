from django.urls import path
from .views import welcome
from .views import get_login_message
from .views import get_search_message
from .views import search_player
from .views import search_team
from .views import get_player_stats
from .views import get_team_stats
from .views import handle_load_db_request

urlpatterns = [
    path('', welcome, name='welcome'),
    path('login-message/', get_login_message, name='login_message'),
    path('search-message/', get_search_message, name='search_message'),
    path('search-player/', search_player, name='search_player'),
    path('search-team/', search_team, name='search_team'),
    path('stats/player/<str:name>/', get_player_stats, name='player_stats'),
    path('stats/team/<str:name>/', get_team_stats, name='team_stats'),
    path('load-database/', handle_load_db_request),
]

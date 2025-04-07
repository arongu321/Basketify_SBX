from django.urls import path
from .views import welcome
from .views import get_ml_predictions_msg
from .views import search_player
from .views import search_team
from .views import get_player_stats
from .views import get_team_stats
from .views import handle_load_db_request

# sets up the routes most features: which Python function to call when
# an HTTP request is sent to the path (1st argument)
urlpatterns = [
    path('', welcome, name='welcome'),  # left for debugging purposes: frontend tests connection by this route
    path('predictions-message/', get_ml_predictions_msg, name='predictions_message'),
    path('search-player/', search_player, name='search_player'),  # FR7
    path('search-team/', search_team, name='search_team'),  # FR8
    path('stats/player/<str:name>/', get_player_stats, name='player_stats'),  # FR9
    path('stats/team/<str:name>/', get_team_stats, name='team_stats'),  # FR11
    path('load-database/', handle_load_db_request, name='load_db'),  # pre-fetch connection obj to MongoDB
]

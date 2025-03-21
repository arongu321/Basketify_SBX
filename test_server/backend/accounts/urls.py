from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('register/', views.UserRegistrationView.as_view(), name='register'),
    path('profile/', views.UserDetailView.as_view(), name='profile'),
    path('set-favorite/', views.SetFavoriteView.as_view(), name='set_favorite'),
    path('get-favorite/', views.GetFavoriteView.as_view(), name='get_favorite'),
]
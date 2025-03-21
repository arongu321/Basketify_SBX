from django.db import models
from django.contrib.auth.models import User


# written by Zach
class UserFavorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorites')
    favorite_type = models.CharField(max_length=10, choices=[('player', 'Player'), ('team', 'Team')])
    favorite_name = models.CharField(max_length=100)

    class Meta:
        unique_together = ('user', 'favorite_type')  # ensures one fave team and one fave player per user in DB

    def __str__(self):
        return f"{self.user.username}'s favorite {self.favorite_type}: {self.favorite_name}"
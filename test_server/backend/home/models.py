from django.db import models

# Create your models here.

# no models used for the stats database (MongoDB)
# we could've used djongo or another MongoDB-Django engine and automated
# some of the fetch/commit operations, but we decided to used cusotmized 
# Django views with pymongo instead

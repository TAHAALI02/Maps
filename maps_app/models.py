from django.db import models

# Create your models here.
class location(models.Model):
    latitude = models.DecimalField()
    longitude = models.DecimalField()
    zoom = models.IntegerField()
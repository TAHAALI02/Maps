from django.db import models

# Create your models here.
class Location(models.Model):
    latitude = models.FloatField()
    longitude = models.FloatField()
    zoom = models.IntegerField()

    def __str__(self):
        return f"({self.latitude}, {self.longitude})"
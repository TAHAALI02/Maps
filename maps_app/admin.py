from django.contrib import admin
from .models import Location
# Register your models here.

class LocationAdmin(admin.ModelAdmin):
    list_display = ['latitude','longitude','zoom']

admin.site.register(Location,LocationAdmin)
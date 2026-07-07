from django import forms

class LocationForm(forms.Form):
    latitude = forms.FloatField()
    longitude = forms.FloatField()
    zoom = forms.IntegerField()
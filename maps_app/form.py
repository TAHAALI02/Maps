from django import forms

class LocationForm(forms.Form):
    latitude = forms.FloatField()
    longitude = forms.FloatField()
    zoom = forms.IntegerField()

from django.contrib.auth.models import User

class signup(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name','last_name','username','email','password']

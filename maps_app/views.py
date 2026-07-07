from django.shortcuts import render
from .form import LocationForm
# Create your views here.
def home(request):
    form = LocationForm()
    latitude= 24.38
    longitude= 46.43
    zoom= 8
    if request.method == 'POST':
        form = LocationForm(request.POST)
        if form.is_valid():
            latitude = form.cleaned_data['latitude']
            longitude = form.cleaned_data['longitude']
            zoom = form.cleaned_data['zoom']
    data = {
        "latitude": latitude,
        "longitude": longitude,
        "zoom": zoom,
    }
    return render(request,'maps_app/home.html',{'data':data,'form':form})
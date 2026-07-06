from django.shortcuts import render

# Create your views here.
def home(request):
    data = {
        "latitude": 24.38,
        "longitude": 46.43,
        "zoom": 5,
    }
    return render(request,'maps_app/home.html',{'data':data})
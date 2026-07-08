from django.shortcuts import render,redirect
from .form import LocationForm,signup
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


def signupview(request):
    form = signup()
    name = "Signup" 
    if request.method == 'POST':
        form = signup(request.POST)
        if form.is_valid(): 
            user = form.save()
            user.set_password(user.password)
            user.save()
            return redirect('login')
    return render(request,'registration/signup.html',{'form':form,'name':name})


from django.contrib.auth.models import User
def adminsignup(request):

    if User.objects.filter(is_superuser = True).exists():
        return render(request,'maps_app/adminalready.html')

    form = signup()
    if request.method == 'POST':
        form = signup(request.POST)
        username = request.POST.get("username")
        form.is_staff = True
        form.is_superuser = True
        data = form.save()
        data.set_password(data.password)

        # this part is for assign as a admin
        user = User.objects.get(username=username)
        user.is_staff = True
        user.is_superuser = True
        user.save()
        redirect('/')

    return render(request,'registration/signup.html',{'form':form,'name':'Admin Signup'})
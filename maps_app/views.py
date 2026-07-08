from django.shortcuts import render,redirect
# from .forms import LocationForm,signup
# Create your views here.
def home(request):
    # form = LocationForm()
    latitude= 24.38
    longitude= 46.43
    zoom= 8
    # if request.method == 'POST':
    #     form = LocationForm(request.POST)
    #     if form.is_valid():
    #         latitude = form.cleaned_data['latitude']
    #         longitude = form.cleaned_data['longitude']
    #         zoom = form.cleaned_data['zoom']
    data = {
        "latitude": latitude,
        "longitude": longitude,
        "zoom": zoom,
    }
    return render(request,'maps_app/home.html',{'data':data})
#
#
# def signupview(request):
#     form = signup()
#     name = "Signup"
#     if request.method == 'POST':
#         form = signup(request.POST)
#         if form.is_valid():
#             user = form.save()
#             user.set_password(user.password)
#             user.save()
#             return redirect('login')
#     return render(request,'registration/signup.html',{'form':form,'name':name})
#
#
# from django.contrib.auth.models import User
# def adminsignup(request):
#
#     if User.objects.filter(is_superuser = True).exists():
#         return render(request,'maps_app/adminalready.html')
#
#     form = signup()
#     if request.method == 'POST':
#         form = signup(request.POST)
#         username = request.POST.get("username")
#         form.is_staff = True
#         form.is_superuser = True
#         data = form.save()
#         data.set_password(data.password)
#
#         # this part is for assign as a admin
#         user = User.objects.get(username=username)
#         user.is_staff = True
#         user.is_superuser = True
#         user.save()
#         redirect('/')
#
#     return render(request,'registration/signup.html',{'form':form,'name':'Admin Signup'})
#

# =================================================================================================




from django.contrib.auth import get_user_model
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.http import require_GET

from .forms import AdminSignupForm, UserSignupForm

User = get_user_model()


def admin_signup(request):
    if User.objects.filter(role=User.ROLE_ADMIN).exists():
        return redirect('login')

    if request.method == "POST":
        form = AdminSignupForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("signup_success")
    else:
        form = AdminSignupForm()
    return render(request, "accounts/admin_signup.html", {"form": form})


def user_signup(request):
    if request.method == "POST":
        form = UserSignupForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("signup_success")
    else:
        form = UserSignupForm()
    return render(request, "accounts/user_signup.html", {"form": form})


def signup_success(request):
    return render(request, "accounts/signup_success.html")


@require_GET
def check_username(request):
    username = request.GET.get("username", "").strip()
    if not username:
        return JsonResponse({"available": False, "message": "Username cannot be empty."})
    if len(username) < 3:
        return JsonResponse({"available": False, "message": "Username must be at least 3 characters."})
    exists = User.objects.filter(username__iexact=username).exists()
    return JsonResponse({
        "available": not exists,
        "message": "Username is already taken." if exists else "Username is available.",
    })

# =========================================================================================
# Login View

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

from .forms import LoginForm


def login_view(request):
    if request.user.is_authenticated:
        return redirect("home")

    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect("home")
            else:
                form.add_error(None, "Invalid username or password.")
    else:
        form = LoginForm()

    return render(request, "accounts/login.html", {"form": form})

@login_required
def logout_view(request):
    logout(request)
    return redirect("login")

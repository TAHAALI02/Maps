from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path("signup/admin/", views.admin_signup, name="admin_signup"),
    path("signup/user/", views.user_signup, name="user_signup"),
    path("signup/success/", views.signup_success, name="signup_success"),
    path("api/check-username/", views.check_username, name="check_username"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
]
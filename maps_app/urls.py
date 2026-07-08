from django.urls import path
from .views import *

urlpatterns = [
    path('', home, name='home'),
    path('signup/', signupview,name='sign'),
    path('onetime/',adminsignup,name='admin')
]
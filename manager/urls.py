from django.urls import path
from manager import views
urlpatterns=[
    path("login",views.login),
    path("login_token",views.login_token),
    path("logout",views.logout)
]
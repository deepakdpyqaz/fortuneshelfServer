from django.urls import path
from manager import views
urlpatterns=[
    path("",views.access_check),
    path("login",views.login),
    path("login_token",views.login_token),
    path("logout",views.logout),
    path("profile/<int:managerId>",views.profile),
    path("all",views.get_all_admins),
    path("reset_password_request",views.resetPasswordRequest),
    path("reset_password",views.resetPassword),
    path("add",views.addManager)
]
from django.urls import path
from user import views
urlpatterns=[
    path("login",views.login,name="user_login"),
    path("signup",views.signupTempUser,name="user_signup"),
    path("logout",views.logout,name="user_logout"),
    path("reset_password",views.resetPassword,name="reset_password"),
    path("login_token",views.loginUsingToken,name="login_token")
]
from django.urls import path
from user import views
urlpatterns=[
    path("login",views.login,name="user_login"),
    path("signup",views.signupTempUser,name="user_signup"),
    path("logout",views.logout,name="user_logout"),
    path("reset_password",views.resetPassword,name="reset_password"),
    path("login_token",views.loginUsingToken,name="login_token"),
    path("billing_profile",views.ProfileBilling.as_view()),
    path("billing_profile/<int:id>",views.ProfileBillingDetails.as_view()),
    path("profile",views.update_user),
    path("reset_password_request",views.resetPasswordRequest),
    path("send_otp",views.send_otp),
    path("message",views.message)
]
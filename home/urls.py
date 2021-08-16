from django.urls import path
from home import views

urlpatterns=[
    path("top_selling",views.top_selling,name="home_top_selling")
]
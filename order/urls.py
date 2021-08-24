from django.urls import path
from order import views
urlpatterns=[
    path("make_order",views.make_order)
]

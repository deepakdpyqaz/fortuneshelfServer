from django.urls import path
from home import views

urlpatterns=[
    path("top_selling",views.top_selling,name="home_top_selling"),
    path("validate_cart",views.validate_cart,name="home_validate_cart"),
    path("filters",views.all_filters,name="home_filters")
]
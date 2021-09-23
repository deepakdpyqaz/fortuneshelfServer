from django.urls import path
from home import views

urlpatterns=[
    path("top_selling",views.top_selling,name="home_top_selling"),
    path("validate_cart",views.validate_cart,name="home_validate_cart"),
    path("filters",views.all_filters,name="home_filters"),
    path("pincode/<str:pincode>",views.pincode,name="home_pincode"),
    path("script",views.runScript,name="home_script"),
    path("delivery_charges",views.getDeliveryCharge),
    path("set_delivery_charges",views.updateDeliveryCharge)
]
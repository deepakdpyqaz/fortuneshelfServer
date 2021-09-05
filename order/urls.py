from django.urls import path
from order import views
urlpatterns=[
    path("make_order",views.make_order),
    path("track_order",views.track_order),
    path("get_orders",views.get_orders),
    path("get_all_orders",views.get_all_orders)
]

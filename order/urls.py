from django.urls import path
from order import views
urlpatterns=[
    path("make_order",views.make_order),
    path("track_order",views.track_order),
    path("get_orders",views.get_orders),
    path("get_all_orders",views.get_all_orders),
    path("order_by_id/<int:orderId>",views.get_order_details),
    path("status/<int:orderId>",views.updateOrderStatus),
    path("coupons/all",views.get_all_coupons),
    path("coupons/create",views.create_coupon),
    path("coupons/<int:couponId>",views.delete_coupon)
]

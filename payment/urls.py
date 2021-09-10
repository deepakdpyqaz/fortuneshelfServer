from django.urls import path
from payment import views
urlpatterns=[
    path("all",views.get_all_payments),
    path("<int:orderId>",views.getPaymentStatus),
    path("get_key",views.getMerchantKey),
    path("success",views.success),
    path("fail",views.fail),
    path("cancel",views.cancel),
    path("apply_coupon/<str:coupon>",views.applyCoupon)
]
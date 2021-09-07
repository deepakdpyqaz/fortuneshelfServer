from django.urls import path
from payment import views
urlpatterns=[
    path("<int:orderId>",views.getPaymentStatus),
    path("get_key",views.getMerchantKey),
    path("success",views.success),
    path("fail",views.fail),
    path("cancel",views.cancel),
]
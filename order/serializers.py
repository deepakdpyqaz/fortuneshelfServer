from rest_framework import serializers
from order.models import Order, Coupon

class OrderSerializer(serializers.ModelSerializer):
    orderId = serializers.SerializerMethodField()
    class Meta:
        model = Order
        fields="__all__"
    def get_orderId(self, obj):
        return Order.START + obj.id

class CouponSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coupon
        fields="__all__"
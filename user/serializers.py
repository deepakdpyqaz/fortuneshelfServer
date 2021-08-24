from rest_framework import serializers
from user.models import User, BillingProfile

class BillingProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = BillingProfile
        exclude = ["userId"]
class UserSerializer(serializers.ModelSerializer):
    billing_profile = BillingProfileSerializer(read_only=True,many=True)
    class Meta:
        model=User
        fields=['id','mobile','email',"name","age","gender","token","billing_profile"]

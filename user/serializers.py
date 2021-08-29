from rest_framework import serializers
from user.models import User, BillingProfile

class BillingProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = BillingProfile
        exclude = ["userId"]
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model=User
        fields=['id','mobile','email',"first_name","last_name","age","gender"]

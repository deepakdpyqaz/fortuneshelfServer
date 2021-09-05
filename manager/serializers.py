from rest_framework import serializers
from manager.models import Manager
class ManagerSerializer(serializers.ModelSerializer):
    class Meta:
        model=Manager
        exclude=["_password"]
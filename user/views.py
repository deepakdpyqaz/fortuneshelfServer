from django.shortcuts import render
from rest_framework.decorators import api_view
from user.models import User
from user.serializers import UserSerializer
from rest_framework.response import Response
from mailService import send_html_mail
# Create your views here.
@api_view(["POST"])
def login(request):
    username = request.data.get("username",None)
    if not username:
        return Response({"status":"fail","message":"Invalid Request params"},status=402)
    user = User.objects.get(email=username)
    send_html_mail("otp",{"message":"1245"},["deepakdpyqaz@gmail.com"])
    serializer = UserSerializer(user)
    return Response(serializer.data)

def signup(request):
    pass

def logout(request):
    pass

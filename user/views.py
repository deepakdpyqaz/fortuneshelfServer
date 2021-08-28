from django.shortcuts import render
from rest_framework.decorators import api_view
from user.models import User, UserUnverified, BillingProfile
from user.serializers import UserSerializer
from rest_framework.response import Response
from mailService import send_html_mail
import random
from django.db.models import Q
import bcrypt
import time
import uuid

# Create your views here.
@api_view(["POST"])
def login(request):
    username = request.data.get("username",None)
    password = request.data.get("password",None)
    if not username or not password:
        return Response({"status":"fail","message":"Invalid Request params"},status=402)
    user = User.objects.filter(Q(email=username)|Q(mobile=username))
    if not user:
        return Response({"status":"fail","message":"Invalid Login Credentials"},status=401)
    user = user.first()
    if not user.verify_password(password):
        return Response({"status":"fail","message":"Invalid Login Credentials"},status=401)
    
    if not user.token:
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(str(time.time()+user.id).encode("utf-8"), salt)
        user.token=hashed
    user.save()
    serializer = UserSerializer(user)
    return Response(serializer.data)

@api_view(["post"])
def loginUsingToken(request):
    token = request.data.get("token",None)
    if not token:
        return Response({"status":"fail","message":"No token provided"},status=400)
    user = User.objects.filter(token=token)
    if not user:
        return Response({"status":"fail","message":"Invalid token"},status=401)
    user = user.first()
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(str(time.time()+user.id).encode("utf-8"), salt)
    user.token = hashed
    serializer = UserSerializer(user)
    user.save()
    return Response(serializer.data,status=200)

@api_view(["post"])
def logout(request):
    token = request.data.get("token")
    if token:
        user = User.objects.filter(token=token)
        if user:
            user = user.first()
            user.token = ""
            user.save()

    return Response({"status":"success"},status=200)

@api_view(["post"])
def signupTempUser(request):
    try:
        first_name = request.data.get("first_name",None)
        last_name = request.data.get("last_name",None)
        email = request.data.get("email",None)
        mobile = request.data.get("mobile",None)
        age = request.data.get("age",None)
        gender = request.data.get("gender","O")
        address = request.data.get("address",None)
        pincode = request.data.get("pincode",None)
        city = request.data.get("city",None)
        district = request.data.get("district",None)
        state = request.data.get("state",None)
        if not (first_name and last_name and gender and email and mobile and age and address and pincode and city and state and district):
            return Response({"status":"fail","message":"Invalid request"},status=400)
        existingUsers = User.objects.filter(Q(mobile=mobile)|Q(email=email))
        if existingUsers:
            return Response({"status":"fail","message":"Mobile or Email already registered"},status=400)
        tempUser = UserUnverified(first_name=first_name,last_name=last_name,email=email,mobile=mobile,age=age,gender=gender,address=address,pincode=pincode,city=city,district=district,state=state,emailOtp=random.randint(10000,99999),mobileOtp=random.randint(10000,99999))
        tempUser.save()
        send_html_mail("otp verification", {"template":"mail/otp.html","data":{"otp":tempUser.emailOtp}},[email])
        return Response({"status":"success","userId":tempUser.id},status=200)
    except Exception as e:
        return Response({"status":"fail","message":"Internal Server Error"},status=500)

@api_view(["post"])
def resetPassword(request):
    otp = request.data.get("otp",None)
    password = request.data.get("password",None)
    userId = request.data.get("userId",None)
    isVerified = request.data.get("isVerified",False)
    if not (otp and password and userId):
        return Response({"status":"fail","message":"Invalid request"},status=400)

    if isVerified==True:
        return Response({"status":"fail","message":"Service Down"},status=500)
    
    else:
        tempUser = UserUnverified.objects.filter(id=userId)
        if not tempUser:
            return Response({"status":"fail","message":"No user with such id"},status=400)
        tempUser=tempUser.first()
        if tempUser.emailOtp == int(otp) or tempUser.mobileOtp==int(otp):
            existingUser = User.objects.filter(Q(email=tempUser.email)|Q(mobile=tempUser.mobile))
            if existingUser:
                return Response({"status":"fail","message":"User already registerd"},status=400)
            try:
                user = User(first_name=tempUser.first_name,last_name=tempUser.last_name,age=tempUser.age,email=tempUser.email,mobile=tempUser.mobile,gender=tempUser.gender)
                user.password = password
                user.save()
                billing_profile = BillingProfile(address=tempUser.address,userId=user,pincode=tempUser.pincode,city=tempUser.city,state=tempUser.state,district=tempUser.district,country="India")
                billing_profile.save()
                tempUser.delete()
                return Response({"status":"success"},status=200)
            except Exception as e:
                return Response({"status":"fail","message":"Internal server Error"},status=500)
        else:
            return Response({"status":"fail","message":"Invalid Otp"},status=400)

    return Response({"status":"fail"},status=500)

def verify_user(func):
    def inner(*args,**kwargs):
        if len(args):
            req = args[0]
            if "authorization" in req.headers:
                token = req.headers.get("authorization")
                user = User.objects.filter(token=token)
                if not user:
                    return Response({"status":"fail","message":"Authorization Required"},status=401)
                user = user.first()
                args[0].user = user
                return func(*args,**kwargs)

            else:
                return Response({"status":"fail","message":"Authorization Required"},status=401)
    return inner

def get_user(token):
    if not token:
        return False,None
    user = User.objects.filter(token=token)
    if not user:
        return False,None
    else:
        return True, user.first()
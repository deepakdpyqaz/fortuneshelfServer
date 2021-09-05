from django.shortcuts import render
from rest_framework.decorators import api_view
from user.models import User, UserUnverified, BillingProfile, Token
from user.serializers import UserSerializer, BillingProfileSerializer
from rest_framework.response import Response
from rest_framework.request import Request
from mailService import send_html_mail, send_sms
import random
from django.db.models import Q
from rest_framework.views import APIView
import bcrypt
import uuid
import datetime
import time

# Create your views here.
@api_view(["POST"])
def login(request):
    username = request.data.get("username", None)
    password = request.data.get("password", None)
    if not username or not password:
        return Response(
            {"status": "fail", "message": "Invalid Request params"}, status=402
        )
    user = User.objects.filter(Q(email=username) | Q(mobile=username))
    if not user:
        return Response(
            {"status": "fail", "message": "Invalid Login Credentials"}, status=401
        )
    user = user.first()
    if not user.verify_password(password):
        return Response(
            {"status": "fail", "message": "Invalid Login Credentials"}, status=401
        )

    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(str(time.time() + user.id).encode("utf-8"), salt)
    token = Token(user=user,token=hashed.decode("utf-8"),created_on=datetime.datetime.now(datetime.timezone.utc))
    token.save()
    serializer = UserSerializer(user)
    response = serializer.data
    response["token"] = token.token
    return Response(response,status=200)


@api_view(["post"])
def loginUsingToken(request):
    token = request.data.get("token", None)
    if not token:
        return Response({"status": "fail", "message": "No token provided"}, status=400)
    token = Token.objects.filter(token=token)
    if not token:
        return Response({"status": "fail", "message": "Invalid token"}, status=401)
    token=token.first()
    if datetime.datetime.now(datetime.timezone.utc) - token.created_on > datetime.timedelta(days=30):
        token.delete()
        return Response({"status":"fail","message":"Token Expired"},status=401)
    user = token.user
    serializer = UserSerializer(user)
    response = serializer.data
    response["token"] = token.token
    return Response(response, status=200)


@api_view(["post"])
def logout(request):
    token = request.data.get("token")
    if token:
        token = Token.objects.filter(token=token)
        if token:
            token.delete()

    return Response({"status": "success"}, status=200)


@api_view(["post"])
def signupTempUser(request):
    try:
        first_name = request.data.get("first_name", None)
        last_name = request.data.get("last_name", None)
        email = request.data.get("email", None)
        mobile = request.data.get("mobile", None)
        age = request.data.get("age", None)
        gender = request.data.get("gender", "O")
        if not (first_name and last_name and gender and email and mobile and age):
            return Response({"status": "fail", "message": "Invalid request"}, status=400)
        existingUsers = User.objects.filter(Q(mobile=mobile) | Q(email=email))
        if existingUsers:
            return Response(
                {"status": "fail", "message": "Mobile or Email already registered"},
                status=400,
            )
        tempUser = UserUnverified(
            first_name=first_name,
            last_name=last_name,
            email=email,
            mobile=mobile,
            age=age,
            gender=gender,
            emailOtp=random.randint(10000, 99999),
            mobileOtp=random.randint(10000, 99999),
            otpGenTime=datetime.datetime.now(datetime.timezone.utc)
        )
        tempUser.save()
        send_html_mail(
            "otp verification",
            {"template": "mail/otp.html", "data": {"otp": tempUser.emailOtp}},
            [email],
        )
        send_sms(
            "otp verification",
            {"type": "Account Verification", "params": {"otp": tempUser.mobileOtp}},
            [tempUser.mobile],
        )
        return Response({"status": "success", "userId": tempUser.id}, status=200)


    except Exception as e:
        return Response({"status":"fail","message":"Internal Server Error"},status=500)


@api_view(["post"])
def resetPassword(request):
    otp = request.data.get("otp", None)
    password = request.data.get("password", None)
    userId = request.data.get("userId", None)
    isVerified = request.data.get("isVerified", False)
    if not (otp and password and userId):
        return Response({"status": "fail", "message": "Invalid request"}, status=400)

    if isVerified == True:
        user = User.objects.filter(id=userId)

        if not user:
            return Response({"status":"fail","message":"No user with given id"},status=400)
        user = user.first()
        if user.generated_on - datetime.datetime.now(datetime.timezone.utc)>datetime.timedelta(minutes=20):
            return Response({"status":"fail","message":"OTP expired"},status=400)
        user.password = password
        user.save()
        try:
            token = Token.objects.filter(user=user).delete()
        except Exception as e:
            return Response({"status": "fail", "message": "Internal Server Error"}, status=500)
        return Response({'status':"successfull"},status=200)

    else:
        tempUser = UserUnverified.objects.filter(id=userId)
        if not tempUser:
            return Response(
                {"status": "fail", "message": "No user with gien id"}, status=400
            )
        tempUser = tempUser.first()
        if tempUser.otpGenTime - datetime.datetime.now(datetime.timezone.utc) > datetime.timedelta(minutes=20):
            tempUser.delete()
            return Response({"status":"fail","message":"OTP expired"},status=400)
        if tempUser.emailOtp == int(otp) or tempUser.mobileOtp == int(otp):
            existingUser = User.objects.filter(
                Q(email=tempUser.email) | Q(mobile=tempUser.mobile)
            )
            if existingUser:
                return Response(
                    {"status": "fail", "message": "User already registerd"}, status=400
                )
            try:
                user = User(
                    first_name=tempUser.first_name,
                    last_name=tempUser.last_name,
                    age=tempUser.age,
                    email=tempUser.email,
                    mobile=tempUser.mobile,
                    gender=tempUser.gender,
                )
                user.password = password
                user.save()
                tempUser.delete()
                return Response({"status": "success"}, status=200)
            except Exception as e:
                return Response(
                    {"status": "fail", "message": "Internal server Error"}, status=500
                )
        else:
            return Response({"status": "fail", "message": "Invalid Otp"}, status=400)

    return Response({"status": "fail"}, status=500)


def verify_user(func):
    def inner(*args, **kwargs):
        if len(args):
            req = args[0]
            for i in range(len(args)):
                if type(args[i]) == Request:
                    req = args[i]
            if "authorization" in req.headers:
                token = req.headers.get("authorization")
                token = Token.objects.filter(token=token)
                if not token:
                    return Response(
                        {"status": "fail", "message": "Authorization Required"},
                        status=401,
                    )
                user = token.first().user
                args[i].user = user
                return func(*args, **kwargs)

            else:
                return Response(
                    {"status": "fail", "message": "Authorization Required"}, status=401
                )

    return inner


def get_user(token):
    if not token:
        return False, None
    token = Token.objects.filter(token=token)
    if not token:
        return False, None
    else:
        return True, token.first().user


class ProfileBilling(APIView):
    @verify_user
    def get(self,request):
        try:
            billingProfiles = BillingProfile.objects.filter(userId=request.user)
            serializer = BillingProfileSerializer(billingProfiles,many=True)
            return Response(serializer.data,status=200)
        except Exception as e:
            return Response({"status":"fail","message":"Internal server error"},status=500)

    @verify_user
    def put(self,request):
        try:
            address = request.data.get("address",None)
            pincode = request.data.get("pincode",None)
            district = request.data.get("district",None)
            city = request.data.get("city",None)
            state = request.data.get("state",None)
            title = request.data.get("title",None)
            if not (address and pincode and district and city and state and title):
                return Response({"status":"fail","message":"Invalid Request"},status=400)
            billingProfile = BillingProfile(title=title,userId=request.user,address=address,pincode=pincode,district=district,city=city,state=state)
            billingProfile.save()
            return Response({"status":"success","profile_id":billingProfile.id  },status=201)
        except Exception as e:
            return Response({"status":'fail',"message":"Internal Server Error"},status=500)


class ProfileBillingDetails(APIView):
    @verify_user
    def delete(self,request,id):
        try:
            billingProfile = BillingProfile.objects.filter(id=id,userId=request.user)
            if not billingProfile:
                return Response({"status":"fail","message":"Billing Profile Not Found"},status=200)
            billingProfile = billingProfile.first()
            billingProfile.delete()
            return Response({"status":"success"},status=200)
        except Exception as e:
            return Response({"status":'fail',"message":"Internal Server Error"},status=500)
    @verify_user
    def post(self,request,id):
        try:
            address = request.data.get("address",None)
            pincode = request.data.get("pincode",None)
            district = request.data.get("district",None)
            city = request.data.get("city",None)
            state = request.data.get("state",None)
            title = request.data.get("title",None)
            if not address and not pincode and not district and not city and not state and not title:
                return Response({"status":"fail","message":"Invalid Request"},status=400)
            billingProfile = BillingProfile.objects.filter(id=id,userId=request.user)
            if not billingProfile:
                return Response({'status':"fail","message":"Billing Profile not found"},status=404)
            billingProfile.address = address
            billingProfile.pincode = pincode
            billingProfile.district = district
            billingProfile.city = city
            billingProfile.state = state
            billingProfile.title = title
            billingProfile.save()
            return Response({"status":"success"},status=200)
        except Exception as e:
            return Response({"status":'fail',"message":"Internal Server Error"},status=500)

@api_view(["get"])
@verify_user
def get_verification_otp(request):
    user = request.user
    email = request.data.get("email",None)
    mobile = request.data.get("mobile",None)
    if not email or not mobile:
        return Response({"status":"fail","message":"Invalid params"},status=400)

    user.otp=random.randint(10000, 99999)
    user.generated_on = datetime.datetime.now(datetime.timezone.utc)
    user.save()
    send_html_mail(
            "otp verification",
            {"template": "mail/verification.html", "data": {"otp": user.otp}},
            [email],
        )
    send_sms(
            "otp verification",
            {"type": "Verification", "params": {"otp": user.otp}},
            [mobile],
        )
    return Response({"status":"success"},status=200)

@api_view(["POST"])
@verify_user
def update_user(request):

    try:
        first_name =request.data.get("first_name",None)
        last_name = request.data.get("last_name",None)
        age = request.data.get("age",None)
        gender = request.data.get("gender",None)

        if not (first_name and last_name and age and gender):
            return Response({"status":"fail","message":"Invalid Request"},status=400)
        
        user = request.user
        user.first_name = first_name
        user.last_name = last_name
        user.age = age
        user.gender = gender
        user.save()
        return Response({"status":"success"},status=200)
    except Exception as e:
        return Response({"status":"fail","message":"Internal Server Error"},status=500)

@api_view(["post"])
def resetPasswordRequest(request):
    try:
        username = request.data.get("username",None)
        if not username:
            return Response({"status":"fail","message":"Invalid Request"},status=400)
        user = User.objects.filter(Q(mobile = username)|Q(email=username))

        if not user:
            return Response({"staus":"fail","message":"No user with given Username"},status=404)
        
        user = user.first()
        user.otp=random.randint(10000, 99999)
        user.generated_on = datetime.datetime.now(datetime.timezone.utc)
        user.save()

        send_html_mail(
            "Reset Password verification",
            {"template": "mail/reset_password.html", "data": {"otp": user.otp}},
            [user.email],
        )
        send_sms(
            "Reset Password verification",
            {"type": "Reset Password", "params": {"otp": user.otp}},
            [user.mobile],
        )
        return Response({"status":"success","userId":user.id},status=200)
    except Exception as e:
        return Response({"status":"fail","message":"Internal Server Error"},status=500)

@api_view(["post"])
def send_otp(request):
    # try:
        isVerified = request.data.get("isVerified",None)
        if isVerified==None:
            return Response({"status":"fail","message":"Invalid request"},status=400)
        if isVerified:
            userId = request.data.get("userId",None)
            if not userId:
                return Response({"status":"fail","message":"Invalid request"},status=400)
            user = User.objects.filter(id=userId)
            if not user:
                return Response({"status":"fail","message":"No record found"},status=400)
            user = user.first()
            user.otp=random.randint(10000, 99999)
            user.generated_on = datetime.datetime.now(datetime.timezone.utc)

            send_html_mail(
                "Reset Password verification",
                {"template": "mail/reset_password.html", "data": {"otp": user.otp}},
                [user.email],
            )
            send_sms(
                "Reset Password verification",
                {"type": "Reset Password", "params": {"otp": user.otp}},
                [user.mobile],
            )
            user.save()
            return Response({"status":"success"},status=200)

        else:
            mobile=request.data.get("mobile",None)
            email = request.data.get("email",None)
            if not mobile or not email:
                return Response({"status":"fail","message":"Invalid request"},status=400)
            user = UserUnverified.objects.filter(Q(mobile=mobile)|Q(email=email))
            if not user:
                return Response({"status":"fail","message":"No record found"},status=400)
            user = user.first()
            user.mobileOtp=random.randint(10000, 99999)
            user.emailOtp = random.randint(10000, 99999)
            user.otpGenTime = datetime.datetime.now(datetime.timezone.utc)
            send_html_mail(
                "otp verification",
                {"template": "mail/otp.html", "data": {"otp": user.emailOtp}},
                [email],
            )
            send_sms(
                "otp verification",
                {"type": "Account Verification", "params": {"otp": user.mobileOtp}},
                [mobile],
            )
            user.save()
            return Response({"status":"success"},status=200)
    # except Exception as e:
    #     return Response({"status":"fail","message":"Could not send otp"},status=500)




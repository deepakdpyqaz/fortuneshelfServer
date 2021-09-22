from django.shortcuts import render
from manager.models import Manager, AdminToken
from manager.serializers import ManagerSerializer
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from django.db.models import Q
from manager.serializers import ManagerSerializer
import datetime
import time
import bcrypt
from mailService import send_html_mail, send_sms
import random
# Create your views here.

def verify_manager(permission):
    def verify_manager_wrapper(func):
        def inner(*args, **kwargs):
            if len(args):
                req = args[0]
                for i in range(len(args)):
                    if type(args[i]) == Request:
                        req = args[i]
                if "authorization" in req.headers:
                    token = req.headers.get("authorization")
                    token = AdminToken.objects.filter(token=token)
                    if not token:
                        return Response(
                            {"status": "fail", "message": "Authorization Required"},
                            status=401,
                        )
                    manager = token.first().manager
                    isPermission = getattr(manager, permission)
                    if isPermission:
                        args[i].manager = manager
                        return func(*args, **kwargs)
                    return Response({"status":"fail","message":"You don't have enough permissions"},status=403)

                else:
                    return Response(
                        {"status": "fail", "message": "Authorization Required"}, status=401
                    )

        return inner
    return verify_manager_wrapper

@api_view(["post"])
def login(request):
    username = request.data.get("username",None)
    password = request.data.get("password",None)

    if not (username and password):
        return Response({"status":"fail","message":"Invalid parameters"},status=400)
    
    manager = Manager.objects.filter(Q(email=username)|Q(mobile=username))
    if not manager:
        return Response({"status":"fail","message":"Invalid Credentials"},status=401)
    manager = manager.first()
    if not manager.verify_password(password):
        return Response({"status":"fail","message":"Invalid Credentials"},status=401)
    serializer = ManagerSerializer(manager)
    response = serializer.data
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(str(time.time() + manager.id).encode("utf-8"), salt)
    token = AdminToken(manager=manager,token=hashed.decode("utf-8"),created_on=datetime.datetime.now(datetime.timezone.utc))
    token.save()
    response["token"]=token.token
    return Response(response,status=200)

@api_view(["post"])
def login_token(request):
    token = request.data.get("token",None)
    if not token:
        return Response({"status":"fail","message":"Invalid request"},status=401)
    admin_token = AdminToken.objects.filter(token=token)
    if not admin_token:
        return Response({"status":"fail","message":"Invalid token"},status=401)
    admin_token = admin_token.first()
    if datetime.datetime.now(datetime.timezone.utc) - admin_token.created_on > datetime.timedelta(days=30):
        token.delete()
        return Response({"status":"fail","message":"Token Expired"},status=401)
    manager = admin_token.manager
    serializer = ManagerSerializer(manager)
    response = serializer.data
    response["token"]=admin_token.token
    return Response(response,status=200)

@api_view(["post"])
def logout(request):
    token = request.data.get("token",None)
    if token:
        Admin_tokens.object.filter(token=token).delete()
    return Response({"status":"success"},status=200)


@api_view(["get"])
@verify_manager(("users"))
def get_all_admins(request):
    managers = Manager.objects.all()
    serializer = ManagerSerializer(managers,many=True)
    return Response(serializer.data,status=200)

@api_view(["GET","POST"])
def profile(request,managerId):
    if  "authorization" in request.headers:
        token = request.headers.get("authorization")
        admin_token = AdminToken.objects.filter(token=token)
        if not admin_token:
            return Response({"status":"fail"},status=401)
        admin_token = admin_token.first()
        manager = admin_token.manager

        if request.method=="GET":
            if manager.users or manager.id==managerId:
                serializer = ManagerSerializer(manager)
                return Response(serializer.data,status=200)
        if request.method=="POST":
            if manager.users or manager.id==managerId:
                first_name = request.data.get("first_name",None)
                last_name = request.data.get("last_name",None)
                users = request.data.get("users",False)
                books = request.data.get("books",False)
                payment = request.data.get('payment',False)
                orders = request.data.get("orders",False)
                coupon = request.data.get("coupon",False)
                if not first_name or not last_name:
                    return Response({"status":"success","message":"Invalid Request"},status=400)
                manager.first_name =first_name
                manager.last_name = last_name
                if manager.users:
                    manager.users=users
                    manager.books=books
                    manager.payment=payment
                    manager.orders=orders
                    manager.coupon=coupon
                manager.save()
                return Response({"status":"success"},status=200)
    return Response({"status":"fail"},status=400)
                


@api_view(["post"])
def resetPasswordRequest(request):
    try:
        username = request.data.get("username",None)
        if not username:
            return Response({"status":"fail","message":"Invalid Request"},status=400)
        manager = Manager.objects.filter(Q(mobile = username)|Q(email=username))

        if not manager:
            return Response({"staus":"fail","message":"No user with given Username"},status=404)
        
        manager = manager.first()
        manager.otp=random.randint(10000, 99999)
        manager.generated_on = datetime.datetime.now(datetime.timezone.utc)
        manager.save()

        send_html_mail(
            "Reset Password verification",
            {"template": "mail/reset_password.html", "data": {"otp": manager.otp}},
            [manager.email],
        )
        send_sms(
            "Reset Password verification",
            {"type": "Reset Password", "params": {"otp": manager.otp}},
            [manager.mobile],
        )
        return Response({"status":"success","managerId":manager.id},status=200)
    except Exception as e:
        return Response({"status":"fail","message":"Internal Server Error"},status=500)
@api_view(["post"])
def resetPassword(request):
    try:
        managerId = request.data.get("managerId",None)
        password  = request.data.get("password",None)
        otp = request.data.get("otp",None)

        if not managerId or not password or not otp:
            return Response({"status":"fail","message":"Invalid Request"},status=400)
        
        manager = Manager.objects.filter(id=managerId)
        if not manager:
            return Response({"status":"fail","message":"Invalid Request"},status=400)
        manager = manager.first()
        if manager.generated_on - datetime.datetime.now(datetime.timezone.utc)>datetime.timedelta(minutes=20):
            return Response({"status":"fail","message":"OTP expired"},status=400)
        if manager.verify_password(password):
            return Response({"status":"fail","message":"New and old password cannot be same"},status=400)
        manager.password=password
        manager.save()
        return Response({"status":"success"},status=200)
    except Exception as e:
        return Response({"status":"fail","message":"Internal Server Error"},status=500)

@api_view(["post"])
def addManager(request):
    try:
        first_name = request.data.get("first_name")
        last_name = request.data.get("last_name")
        email = request.data.get("email")
        mobile = request.data.get("mobile")
        users = request.data.get("users",False)
        orders = request.data.get("orders",False)
        payment = request.data.get("payment",False)
        books = request.data.get("books",False)
        manager = Manager.objects.filter(Q(email=email)|Q(mobile=mobile))
        if manager:
            return Response({"status":"fail","message":"email of phone already registered"},status=400)
        if not first_name or not last_name or not email or not mobile:
            return Response({"status":"fail","message":"Invalid Request"},status=400)
        
        manager = Manager(first_name=first_name,last_name=last_name,email=email,mobile=mobile,users=users,orders=orders,payment=payment,books=books)
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(str(time.time()).encode("utf-8"), salt)
        password = hashed.decode("utf-8")[:10]
        manager.password = password
        manager.save()
        send_html_mail("Invitation",  {"template": "mail/invite_admin.html", "data": {"password":password }}, [email])
        send_sms(
                "Invitation",
                {"type": "Invitation", "params": {"password": password}},
                [mobile],
            )

        return Response({"status":"success"},status=200)
    except Exception as e:
        return Response({"status":"fail","message":"Internal Server Error"},status=500)
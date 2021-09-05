from django.shortcuts import render
from manager.models import Manager, AdminToken
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from django.db.models import Q
from manager.serializers import ManagerSerializer
import datetime
import time
import bcrypt
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
    return Response(serializer.data,status=200)

@api_view(["post"])
def logout(request):
    token = request.data.get("token",None)
    if token:
        Admin_tokens.object.filter(token=token).delete()
    return Response({"status":"success"},status=200)



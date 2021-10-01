from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from book.views import getBooksFromDb, books_by_ids
from home.models import Utilities,Pincode, Banner
from home.serializers import BannerSerializer
from rest_framework.views import APIView
from django.db.models import Q
import requests
import logging
import json
from functools import lru_cache
from manager.views import verify_manager
from redisClient import Client
# Create your views here.


@api_view(["GET"])
def healthCheck(request):
    return Response({"status":"OK","message":"Server is running"},status=200)
@api_view(["GET"])
def top_selling(request):
    try:
        top_selling = Client.getkey("top_selling")
        if top_selling:
            return Response(top_selling)
        else:
            top_selling = getBooksFromDb(1, 11, "-view_count")
            Client.setkey("top_selling",top_selling)
            return Response(top_selling)    
    except Exception as e:
        logging.error(str(e))
        return Response({"status":"fail","message":"Internal Server Error"},status=500)

def all_filters_from_db():
    languages=Client.getkey("languages")
    categories = Client.getkey("categories")
    if languages and categories:
        return {"languages":languages,"categories":categories}

    filters = Utilities.objects.filter(Q(key="languages")|Q(key="categories"))
    response = {}
    for filter in filters:
        response.update(filter.value)

        Client.setkey(filter.key,filter.value.get(filter.key))
    return response
@api_view(["GET"])
def all_filters(request):
    try:
        response = all_filters_from_db()
        return Response(response,status=200)
    except Exception as e:
        logging.error(str(e))
        return Response({"status":"fail","message":"Internal Server Error"},status=500)



def validate_item(item1,item2):
    try:
        for key in item1.keys():
            if (item1[key]!=item2[key]):
                return False
        return True
    except:
        return False
@api_view(["POST"])
def validate_cart(request):
    try:
        cart = request.data.get("cart",None)
        if not cart:
            return Response({"status":"success","validated":True,"cart":{}},status=200)
        server_cart_data = books_by_ids(cart.keys())
        server_cart={}
        validated_data=True
        for item in server_cart_data:
            validated_data = validated_data and validate_item(item,cart[str(item["book_id"])])
            server_cart[str(item["book_id"])]=item
            server_cart[str(item["book_id"])]["stock"]=cart[str(item["book_id"])]["stock"]
            server_cart[str(item["book_id"])]["bookId"]=item["book_id"]
        return Response({'status':"success","validate":validated_data,"cart":server_cart})
    except Exception as e:
        logging.error(str(e))
        return Response({"status":"fail","message":"Internal Server Error"},status=500)
@api_view(["GET"])
def pincode(request,pincode):
    try:
        pincode = Pincode.objects.filter(pincode=pincode)
        if pincode:
            return Response({"status":"success","state":pincode[0].state,"district":pincode[0].district.capitalize()})
        else:
            return Response({"status":"fail","state":None,"district":None})

    except Exception as e:
        logging.error(str(e))
        return Response({"status":"fail","message":"Internal Server Error"},status=500)

@api_view(["GET"])
def runScript(request):
    try:
        with open("pincode.json","r") as f:
            codes = json.load(f)
        fullData =[]
        for code,data in codes.items():
            pincode = Pincode(pincode=code,state=data.get("state"),district=data.get("district"))
            fullData.append(pincode)
        objs = Pincode.objects.bulk_create(fullData)
        return Response({"status":'success',"len":len(objs)},status=200)
    except Exception as e:
        logging.error(str(e))
        return Response({"status":"fail","message":"Internal Server Error"},status=500)



def getDeliveryChargeFromDb():
    delivery_charge = Client.getkey("delivery_charge")
    if delivery_charge:
        return float(delivery_charge)
    delivery_charge = Utilities.objects.get(key="delivery_charges")
    Client.setkey("delivery_charge", delivery_charge.value.get("delivery_charge"))
    return float(delivery_charge.value.get("delivery_charge"))

def getCodChargeFromDb():
    cod_charges = Client.getkey("cod_charges")
    if cod_charges:
        return cod_charges
    cod_charges = Utilities.objects.get(key="cod_charges")
    Client.setkey("cod_charges",cod_charges.value.get("cod_charges"))
    return cod_charges.value.get("cod_charges")
@api_view(["GET"])
def getDeliveryCharge(request):
    return Response({"status":"success","delivery_charges":getDeliveryChargeFromDb(),"cod_charges":getCodChargeFromDb()},status=200)

@api_view(["post"])
@verify_manager("books")
def updateDeliveryCharge(request):
    try:
        delivery = request.data.get("delivery_charges",None)
        if not delivery:
            return Response({"status":"fail","message":"Invalid request"},status=400)
        delivery_charge = Utilities.objects.get(key="delivery_charges")
        delivery_charge.value = {"delivery_charge":float(delivery)}
        delivery_charge.save()
        Client.setkey("delivery_charge",float(delivery_charge.value.get("delivery_charge")))
        return Response({"status":"success"},status=200)
    except Exception as e:
        logging.error(str(e))
        return Response({"status":"fail","message":"Internal Server Error"},status=500)


# Banner
class BannerById(APIView):
    def put(self,request,id):
        banner = Banner.objects.filter(id=id)
        if not banner:
            return Response({"status":"fail","message":"No banner with said Id"},status=404)
        banner = banner.first()
        banner.title = title
        banner.link = link

        if request.FILES:
            banner.picture = picture
        banner.save()
        return Response({"status":"success"})

from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from book.views import getBooksFromDb, books_by_ids
from home.models import Utilities
from django.db.models import Q
import requests
import logging
# Create your views here.
@api_view(["GET"])
def top_selling(request):
    try:
        return Response(getBooksFromDb(1,11,"-view_count"))    
    except Exception as e:
        logging.error(str(e))
        return Response({"status":"fail","message":"Internal Server Error"},status=500)

@api_view(["GET"])
def all_filters(request):
    try:
        filters = Utilities.objects.filter(Q(key="languages")|Q(key="categories"))
        response = {}
        for filter in filters:
            response.update(filter.value)
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
        r = requests.get("https://api.postalpincode.in/pincode/"+pincode)
        response = r.json()[0]
        if response["Status"]=="Success":
            state = response["PostOffice"][0]["State"]
            district = response["PostOffice"][0]["District"]
            return Response({"status":"success","state":state,"district":district},status=200)
        return Response({"status":"fail","state":None,"district":None})
    except Exception as e:
        logging.error(str(e))
        return Response({"status":"fail","message":"Internal Server Error"},status=500)
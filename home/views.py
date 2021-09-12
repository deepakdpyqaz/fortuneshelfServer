from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from book.views import getBooksFromDb, books_by_ids
# Create your views here.
@api_view(["GET"])
def top_selling(request):
    return Response(getBooksFromDb(1,11,"price"))    

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
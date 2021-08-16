from django.shortcuts import render
from rest_framework.decorators import api_view
from book.models import Book
from book.serializers import BookSerializer
from rest_framework.response import Response
import csv
# Create your views here.
@api_view(["GET"])
def getBooks(request):
    try:
        page_number = int(request.query_params.get("page_number",1))
        per_page = int(request.query_params.get("per_page",25))
        order_by = request.query_params.get("order_by","id")
        isDescending = bool(request.query_params.get("isDescending",False))
        low_price = int(request.query_params.get("low_price",0))
        high_price = int(request.query_params.get("high_price",0))
        language = request.query_params.get("language",None)
    except Exception as e:
        return Response({"status":"fail","Message":str(e)},status=400)
    return Response(getBooksFromDb(page_number,per_page,order_by,isDescending,low_price,high_price,language))

def getBooksFromDb(page_number,per_page,order_by,desc=False,low_price=None,high_price=None,language=None):
    if desc:
        order_by="-"+order_by
    filters={}
    if language:
        filters["language"]=language
    if low_price:
        filters["price__gte"]=low_price
    if high_price:
        filters["price__lte"] = high_price
    books = Book.objects.filter(**filters).order_by(order_by)[(page_number-1)*per_page:page_number*per_page-1:]
    serializer = BookSerializer(books,many=True)
    return serializer.data

def addBooks(request):
    # bookList=[]
    # with open("data.csv", encoding="utf8") as f:
    #     rowReader = csv.reader(f)
    #     i=0
    #     for row in rowReader:
    #         if i==0:
    #             i+=1
    #             continue
    #         if(row[0]):
    #             price = row[5][:len(row[5])-2]
    #             if not price:
    #                 price=100
    #             book = Book(title=row[2],price=price,author="default",language=row[3].lower(),dimension=row[6],description=row[7],weight=price)
    #             bookList.append(book)
    # objs = Book.objects.bulk_create(bookList)
    return Response({"Message":"Success"})

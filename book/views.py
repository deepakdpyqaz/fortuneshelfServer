from django.shortcuts import render
from rest_framework.decorators import api_view
from book.models import Book
from book.serializers import BookSerializer, FullBookSerializer
from rest_framework.response import Response
import csv
import time
from django.db.models import Q
import os
import threading
from threading import Thread
from django.contrib.postgres.search import  SearchQuery, SearchRank, SearchVector


class updateBookView(threading.Thread):
    def __init__(self,booklst):
        self.booklst=booklst
        threading.Thread.__init__(self)
    def run(self):
        for book in self.booklst:
            book.view_count = book.view_count+1
            book.save()

def updateBookViewRecord(booklst):
    updateBookView(booklst).start()



# Create your views here.
@api_view(["GET"])
def getBooks(request):
    try:
        page_number = int(request.query_params.get("page_number",1))
        per_page = int(request.query_params.get("per_page",25))
        order_by = request.query_params.get("order_by","-view_count")
        isDescending = bool(request.query_params.get("isDescending",False))
        low_price = int(request.query_params.get("low_price",0))
        high_price = int(request.query_params.get("high_price",0))
        language = request.query_params.get("language",None)
    except Exception as e:
        return Response({"status":"fail","Message":str(e)},status=400)
    try:
        return Response(getBooksFromDb(page_number,per_page,order_by,isDescending,low_price,high_price,language))
    except Exception as e:
        return Response({"status":"fail","message":"Internal Server Error"},status=500)

def getBooksFromDb(page_number,per_page,order_by,desc=False,low_price=None,high_price=None,language=None):
    if not order_by:
        order_by="view_count"
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

# def addBooks(request):
#     bookList=[]
#     with open("data.csv", encoding="utf8") as f:
#         rowReader = csv.reader(f)
#         i=0
#         for row in rowReader:
#             if i==0:
#                 i+=1
#                 continue
#             if(row[0]):
#                 price = row[5][:len(row[5])-2]
#                 if not price:
#                     price=100
#                 book = Book(title=row[2],price=price,author="default",language=row[3].lower(),dimension=row[6],description=row[7],weight=price)
#                 bookList.append(book)
#     objs = Book.objects.bulk_create(bookList)
#     return Response({"Message":"Success"})


@api_view(["GET"])
def searchBookByKeyWords(request):
    queryString = request.query_params.get("query",None)
    if not queryString:
        return Response([],status=200)
    vector = SearchVector("title",weight='A')+SearchVector("description",weight='B') + SearchVector("language",weight='C')
    query = SearchQuery(queryString)
    booklist = Book.objects.annotate(rank=SearchRank(vector, query)).filter(rank__gte=0.3).order_by('-rank')
    serializer = BookSerializer(booklist,many=True)

    return Response(serializer.data,status=200)

@api_view(["GET"])
def book_by_id(request,bookid):
    START = 1000000
    book = Book.objects.filter(id=bookid-START)
    if book:
        updateBookViewRecord(book)
        serializer = FullBookSerializer(book[0])
        return Response(serializer.data,status=200)
    else:
        return Response({"status":"fail","message":"Book not found"},404)

def books_by_ids(bookids,obj=False):
    START = 1000000
    bookids = list(map(lambda x:float(x)-START,bookids))

    books = Book.objects.filter(id__in=bookids).order_by("id")
    updateBookViewRecord(books)
    if obj:
        return books
    else:
        serializer= BookSerializer(books,many=True)
        return serializer.data


def getLanguage(text):
    langList = ["hindi","english","marathi","bangali","nepali","oriya","other book","gujarati","kannada","malayalam","tamil","telugu"]
    for item in langList:
        if item in text:
            return item
    return "GIBRISH"

# @api_view(["GET"])
# def upadatePic(request):
#     print(os.getcwd())
#     os.chdir("media/")
#     images = os.listdir()
#     for i in range(len(images)):
#         img=images[i]
#         img = ".".join(img.split(".")[:-1])
#         lst = img.split(" ")
#         images[i] = " ".join(lst[:-1]),lst[-1],images[i]
#     count=0
#     for img,lang,original in images:
#         if img and img!="default":
#             lang = getLanguage(lang.lower())
#             book = Book.objects.filter(title__icontains=img,language__icontains=lang)
#             for bk in book:
#                 bk.picture=original
#                 bk.save()
#             count+=len(book)
#     return Response({"status":"sucess","count":count})

def manageStock(bookDetails):
    books = books_by_ids(bookDetails.keys(),obj=True)
    for bk in books:
        if bk.max_stock<bookDetails[str(bk.bookId)]:
            return False,{"message":f"{bk.title} out of stock"}
    for bk in books:
        bk.max_stock = bk.max_stock-bookDetails[str(bk.bookId)]
        bk.save()
    serializer = BookSerializer(books,many=True)
    return True,{"data":serializer.data}


from django.shortcuts import render
from rest_framework.decorators import api_view
from book.models import Book
from book.serializers import BookSerializer, FullBookSerializer
from rest_framework.response import Response
from rest_framework.views import APIView
import csv
import time
from django.db.models import Q
import os
import threading
from threading import Thread
from django.contrib.postgres.search import  SearchQuery, SearchRank, SearchVector
from manager.views import verify_manager


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

def books_by_ids(bookids,obj=False,record=True):
    START = 1000000
    bookids = list(map(lambda x:float(x)-START,bookids))

    books = Book.objects.filter(id__in=bookids).order_by("id")
    if record:
        updateBookViewRecord(books)
    if obj:
        return books
    else:
        serializer= BookSerializer(books,many=True)
        return serializer.data



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

@api_view(["put"])
@verify_manager("books")
def create_book(request):
    try:
        title = request.data.get("title",None)
        price = request.data.get("price",None)
        author = request.data.get("author",None)
        language = request.data.get("language",None)
        discount = request.data.get("discount",None)
        dimension = request.data.get("dimension",None)
        weight = request.data.get("weight",None)
        description = request.data.get("description",None)
        picture = request.FILES.get("picture",None)
        delivery_factor = request.data.get("delivery_factor",1)

        if not (title and price  and language and dimension and weight and description and picture):
            return Response({"status":"fail","message":"Invalid request"},status=400)
        
        book = Book(title=title,price=price,author=author,language=language,discount=discount,dimension=dimension,weight=weight,description=description,picture=picture,delivery_factor=delivery_factor)
        book.save()
        return Response({"status":"success","bookId":book.bookId},status=201)
    except Exception as e:
        return Response({"status":"fail","message":"Internal server error"},status=500)

class BookDetails(APIView):
    @verify_manager("books")
    def post(self,request,bookId):
        try:
            title = request.data.get("title",None)
            price = request.data.get("price",None)
            author = request.data.get("author",None)
            language = request.data.get("language",None)
            discount = request.data.get("discount",None)
            dimension = request.data.get("dimension",None)
            weight = request.data.get("weight",None)
            description = request.data.get("description",None)
            picture = request.FILES.get("picture",None)
            delivery_factor = request.data.get("delivery_factor",1)
            if not (title and price  and language and dimension and weight and description and picture):
                return Response({"status":"fail","message":"Invalid request"},status=400)
            
            book = Book.objects.filter(id=Book.getId(bookId))
            if not book:
                return Response({"status":"fail","message":"Book not found"},status=404)
            book = book.first()
            book.title = title
            book.price = price
            book.author = author
            book.language = language
            book.discount = discount
            book.dimension = dimension
            book.weight = weight
            book.description = description
            book.picture = picture
            book.delivery_factor = delivery_factor
            book.save()
            return Response({"status":"success"},status=200)
        except Exception as e:
            return Response({"status":"fail","message":"Internal Server Error"},status=500)

    @verify_manager("books")
    def delete(self,request,bookId):
        try:
            book = Book.objects.filter(id=Book.getId(bookId))
            if not book:
                return Response({"status":"fail","message":"Book not found"},status=404)
            book.delete()
            return Response({"status":"success"},status=200)
        except Exception as e:
            return Response({"status":"fail","message":"Internal Server Error"},status=500)



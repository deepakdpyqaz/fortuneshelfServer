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
from django.conf import settings
from django.db.models import Subquery
import logging
from manager.views import get_manager
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
        category = request.query_params.get("category",None)
        delivery_free = request.query_params.get("delivery_free",False)
    except Exception as e:
        return Response({"status":"fail","Message":str(e)},status=400)
    try:
        return Response(getBooksFromDb(page_number,per_page,order_by,isDescending,low_price,high_price,language,category,delivery_free))
    except Exception as e:
        logging.error(str(e))
        return Response({"status":"fail","message":"Internal Server Error"},status=500)

def getBooksFromDb(page_number,per_page,order_by,desc=False,low_price=None,high_price=None,language=None,category=None,delivery_free=False):
    if not order_by:
        order_by="-view_count"
    if desc:
        order_by="-"+order_by
    filters={}
    if language:
        filters["language"]=language
    if low_price:
        filters["price__gte"]=low_price
    if delivery_free and delivery_free=="true":
        filters["delivery_factor"]=0
    if high_price:
        filters["price__lte"] = high_price
    if category:
        filters["category"] = category.lower()
    books = Book.objects.filter(outdated=False,**filters).order_by(order_by)[(page_number-1)*per_page:page_number*per_page:]
    serializer = BookSerializer(books,many=True)
    return serializer.data



@api_view(["GET"])
def searchBookByKeyWords(request):
    try:
        queryString = request.query_params.get("query",None)
        if not queryString:
            return Response([],status=200)
        vector = SearchVector("title",weight='A')+SearchVector("language",weight='B') + SearchVector("description",weight='C')
        query = SearchQuery(queryString)
        booklist = Book.objects.annotate(rank=SearchRank(vector, query)).filter(outdated=False,rank__gte=0.3).order_by('-rank')
        serializer = BookSerializer(booklist,many=True)

        return Response(serializer.data,status=200)
    except Exception as e:
        logging.error(str(e))
        return Response({"status":"fail","message":"Internal Server Error"},status=500)

@api_view(["GET"])
def book_by_id(request,bookid):
    try:
        START = 1000000
        outdatedAccess=False
        print(request.headers)
        if "authorization" in request.headers:
            op_status,manager = get_manager(request.headers.get("authorization",""))
            if op_status and manager.books:
                outdatedAccess=True
        if outdatedAccess:
            book = Book.objects.filter(id=bookid-START)
        else:
            book = Book.objects.filter(id=bookid-START,outdated=False)
        if book:
            updateBookViewRecord(book)
            serializer = FullBookSerializer(book[0])
            return Response(serializer.data,status=200)
        else:
            return Response({"status":"fail","message":"Book not found"},404)
    except Exception as e:
        logging.error(str(e))
        return Response({"status":"fail","message":"Internal Server Error"},status=500)

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



def manageStock(bookDetails,deduct=True):
    books = books_by_ids(bookDetails.keys(),obj=True)
    for bk in books:
        if bk.max_stock<bookDetails[str(bk.bookId)]:
            return False,{"message":f"{bk.title} out of stock"}
    if deduct:
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
        language = request.data.get("language",None)
        discount = request.data.get("discount",None)
        length = request.data.get("length",None)
        breadth = request.data.get("breadth",None)
        height = request.data.get("height",None)
        weight = request.data.get("weight",None)
        description = request.data.get("description",None)
        picture = request.FILES.get("picture",None)
        delivery_factor = request.data.get("delivery_factor",1)
        stock = request.data.get('max_stock',None)
        category = request.data.get("category",None)
        if not (title and price  and language and length and breadth and height and weight and description and picture and stock):
            return Response({"status":"fail","message":"Invalid request"},status=400)
        
        book = Book(title=title,price=price,language=language.lower(),discount=discount,length=length,breadth=breadth,height=height,weight=weight,description=description,picture=picture,delivery_factor=delivery_factor,max_stock=stock,category=category.lower())
        book.save()
        return Response({"status":"success","bookId":book.bookId},status=201)
    except Exception as e:
        logging.error(str(e))
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
            length = request.data.get("length",None)
            breadth = request.data.get("breadth",None)
            height = request.data.get("height",None)
            weight = request.data.get("weight",None)
            description = request.data.get("description",None)
            stock = request.data.get("max_stock",None)
            category = request.data.get("category",None)
            picture = request.FILES.get("picture",None)
            delivery_factor = request.data.get("delivery_factor",1)
            if not (title and price  and language and length and breadth and height and weight and description and stock):
                return Response({"status":"fail","message":"Invalid request"},status=400)
            
            book = Book.objects.filter(id=Book.getId(bookId))
            if not book:
                return Response({"status":"fail","message":"Book not found"},status=404)
            book = book.first()
            if (book.price == float(price)) and (book.discount==float(discount)) and (book.delivery_factor==float(delivery_factor)) and (book.weight==float(weight)):
                book.title = title
                book.price = price
                book.author = author
                book.language = language
                book.discount = discount
                book.length = length
                book.breadth = breadth
                book.height = height
                book.weight = weight
                book.description = description
                if picture:
                    book.picture = picture
                book.delivery_factor = delivery_factor
                book.max_stock = stock
                book.category = category
                book.save()
                return Response({"status":"success","created":False},status=200)
            else:
                book.outdated=True
                book.save()
                newBook = Book(title=title,price=price,language=language,discount=discount,length=length,breadth=breadth,height=height,weight=weight,description=description,delivery_factor=delivery_factor,max_stock=stock,category=category)
                if picture:
                    newBook.picture = picture
                else:
                    newBook.picture=book.picture
                newBook.save()
                return Response({"status":"success","bookId":newBook.bookId,"created":True},status=200)
        except Exception as e:
            logging.error(str(e))
            return Response({"status":"fail","message":"Internal Server Error"},status=500)

    @verify_manager("books")
    def delete(self,request,bookId):
        try:
            book = Book.objects.filter(id=Book.getId(bookId))
            if not book:
                return Response({"status":"fail","message":"Book not found"},status=404)
            book = book.first()
            book.outdated=True
            book.save()
            return Response({"status":"success"},status=200)
        except Exception as e:
            logging.error(str(e))
            return Response({"status":"fail","message":"Internal Server Error"},status=500)


@api_view(["GET"])
@verify_manager("books")
def allBooks(request):
    try:
        books = Book.objects.values_list("id","title").filter(outdated=False).order_by("-id")
        response = [{"bookId":book[0]+Book.START,"title":book[1]} for book in books]
        return Response({"status":"success","data":response},status=200)
    except Exception as e:
        logging.error(str(e))
        return Response({"status":"fail","message":"Internal Server Error"},status=500)

@api_view(["GET"])
def runScript(request):
    if not settings.DEBUG:
        return Response({},status=404)
        
    # os.chdir("media/images")
    # images = os.listdir()
    # success=0
    # fail=0
    # data=[]
    # try:
    #     for img in images:
    #         imgorg=img
    #         img = ".".join(img.split(".")[:-1])
    #         bk = Book.objects.filter(title=img)
    #         if not bk:
    #             split = img.split("(")
    #             if len(split)>=2:
    #                 img,lang="".join(split[:-1]),split[-1]
    #                 img = img.strip(" ")
    #                 lang = lang.strip(" ")
    #                 lang = lang.strip(")")
    #                 bk = Book.objects.filter(title=img,language__icontains=lang)
    #                 if not bk:
    #                     fail+=1
    #                     data.append(imgorg)
    #                 else:
    #                     bk=bk.first()
    #                     bk.picture = f"books/{imgorg}"
    #                     success+=1
    #                     bk.save()
    #             else:
    #                 fail+=1
    #                 data.append(imgorg)
    #         else:
    #             bk=bk.first()
    #             bk.picture = f"books/{imgorg}"
    #             success+=1
    #             bk.save()
    #     return Response({"status":"success","success":success,"fail":fail,"data":data})
    # except Exception as e:
    #     return Response({'status':"fail","error":str(e)})
    with open("data-new.csv",encoding="utf-8",newline="\n") as f:
        reader = csv.reader(f,delimiter=",")
        success=0
        fail = 0
        failList={}
        escape=True
        added=0
        i=0
        for row in reader:
            i+=1
            if escape:
                escape=False
                continue
            try:
                id = (row[0])
                title = row[1]
                language = row[2].lower()
                if not id and not title and not language:
                    continue
                weight = int(row[3])
                price = int(row[4])
                discount = int(row[5])
                delivery_factor = int(row[6])
                max_stock = int(row[7])
                category = row[8]
                if not category:
                    category=None
                if not id:
                    bk = Book(title=title,language=language.lower(),weight=int(weight),price=int(price),discount=int(discount),delivery_factor=int(delivery_factor),category=category,max_stock=int(max_stock),length=30,breadth=30,height=30,picture=title+".jpg",description=title)
                    added+=1
                else:
                    bk = Book.objects.filter(id=id)
                    bk = bk.first()
                if not bk:
                    fail+=1
                    failList[id]=title, "bk not found"
                    continue
                bk.title = title
                bk.language=language
                bk.weight=weight
                bk.price=price
                bk.discount=discount
                bk.delivery_factor = delivery_factor
                bk.max_stock = max_stock
                if category:
                    bk.category=category
                else:
                    bk.category=None
                bk.save()
                success+=1
            except Exception as e:
                fail+=1
                failList["error"+str(i)]=str(e)
        return Response({"success":success,"fail":fail,"data":failList,"added":added},status=200)
        if(counter%3==0):
            bk.category="gita"
        elif(counter%3==1):
            bk.category="set"
        else:
            bk.category="bhagavatam"
        bk.save()
    return Response({"status":"Done"})
    books = Book.objects.all()
    for book in books:
        book.dimension = book.dimension.replace(chr(215),"x")
        lst = list(map(lambda x:x.strip(),book.dimension[:-2:].split("x")))
        if(len(lst)>0 and lst[0].isdecimal()):
            book.length=lst[0]
        if(len(lst)>1 and lst[1].isdecimal()):
            book.breadth=lst[1]
        if(len(lst)>2 and lst[2].isdecimal()):
            book.height=lst[2]
        book.save()
    return Response({"status":"Done"},status=200)


@api_view(["GET"])
def update_books(request):
    if not settings.DEBUG:
        return Response({},status=404)
    books = Book.objects.all()
    for book in books:
        if book.category:
            book.category = book.category.lower()
            book.save()
    return Response({"status":"success"},status=200)


@api_view(["get"])
def searchSuggestions(request):
    try:
        query = request.query_params.get("query")
        books = Book.objects.values_list("title","picture").filter(title__icontains=query).order_by("-view_count")[:5]
        response = []
        for counter,bk in enumerate(books):
            response.append({"title":bk[0],"picture":settings.MEDIA_URL+bk[1],"index":counter});
        return Response(response,status=200)
    except Exception as e:
        logging.error(e)
        return Response({"status":"fail","message":"Internal Server Error"},status=500)


@api_view(["get"])
def similarBooks(request):
    try:
        id = request.query_params.get("id",None)
        if not id:
            return Response({'status':"fail","message":"Invalid request"},status=400)
        book = Book.objects.filter(id=Book.getId(id)).first()
        books = Book.objects.filter(language=book.language,category=book.category,outdated=False)[:10]
        serializer = BookSerializer(books,many=True)
        return Response(serializer.data,status=200)
    except Exception as e:
        logging.error(str(e))
        return Response({"status":"fail","message":"Internal Server Error"},status=500)

@api_view(["GET"])
def category_books(request,category):
    try:
        books = Book.objects.filter(category=category,outdated=False).order_by("-view_count")[:10]
        if len(books)<5:
            return Response({"books":[]},status=200)
        else:
            serializer = BookSerializer(books,many=True)
            return Response({"books":serializer.data},status=200)
    except Exception as e:
        logging.error(e)
        return Response({"status":"fail","message":"Internal Server Error"},status=500)

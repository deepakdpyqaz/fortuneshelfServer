from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from book.views import getBooksFromDb
# Create your views here.
@api_view(["GET"])
def top_selling(request):
    return Response(getBooksFromDb(1,10,"price"))    

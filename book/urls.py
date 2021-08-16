from django.urls import path
from . import views
urlpatterns=[
    path("",views.getBooks,name="book_getBooks"),
    path("add",views.addBooks,name="add_books")
]
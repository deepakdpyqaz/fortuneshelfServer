from django.urls import path
from . import views
urlpatterns=[
    path("",views.getBooks,name="book_getBooks"),
    path("book_by_id/<int:bookid>",views.book_by_id,name="book_by_id"),
    path("add",views.addBooks,name="add_books"),
    path("search",views.searchBookByKeyWords,name="search_books"),
    path("update",views.upadatePic)
]
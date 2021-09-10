from django.urls import path
from . import views

urlpatterns=[
    path("",views.getBooks,name="book_getBooks"),
    path("<int:bookId>",views.BookDetails.as_view()),
    path("book_by_id/<int:bookid>",views.book_by_id,name="book_by_id"),
    path("search",views.searchBookByKeyWords,name="search_books"),
    path("add",views.create_book),
    path("all",views.allBooks),
    path("script",views.update_books)
]
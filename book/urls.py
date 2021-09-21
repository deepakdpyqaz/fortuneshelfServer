from django.urls import path
from . import views

urlpatterns=[
    path("",views.getBooks,name="book_getBooks"),
    path("<int:bookId>",views.BookDetails.as_view()),
    path("book_by_id/<int:bookid>",views.book_by_id,name="book_by_id"),
    path("search",views.searchBookByKeyWords,name="search_books"),
    path("add",views.create_book),
    path("all",views.allBooks),
    path("search_suggestions",views.searchSuggestions),
    path("get_similar",views.similarBooks),
    path("script",views.runScript),
    path("update",views.update_books),
    path("categories/<str:category>",views.category_books)
]
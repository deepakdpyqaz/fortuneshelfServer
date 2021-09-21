import logging
from book.models import Book
from home.models import Utilities
def categorySchedular():
    try:
        categories = Book.objects.values_list("category").distinct()
        categoryKey = Utilities.objects.get(key="categories")
        categoryKey.value={"categories":[item for item, in categories.all() ]}
        categoryKey.save()
        logging.debug("Success")
    except Exception as e:
        logging.error("Error "+str(e))
    
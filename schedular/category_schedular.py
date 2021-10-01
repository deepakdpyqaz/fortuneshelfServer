import logging
from book.models import Book
from home.models import Utilities
from home.views import all_filters_from_db
from datetime import timedelta,datetime
from redisClient import Client
def categorySchedular():
    try:
        categories = Book.objects.values_list("category").filter(category__isnull=False).distinct()
        categoryKey = Utilities.objects.get(key="categories")
        categoryKey.value={"categories":[item for item, in categories.all() ]}
        Client.setkey("categories",categoryKey.value.get("categories"),timedelta(days=1))
        categoryKey.save()
    except Exception as e:
        logging.error(str(e))

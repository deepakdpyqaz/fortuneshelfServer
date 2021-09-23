import logging
from book.models import Book
from home.models import Utilities
from home.views import all_filters_from_db
def categorySchedular():
    try:
        categories = Book.objects.values_list("category").filter(category__isnull=False).distinct()
        categoryKey = Utilities.objects.get(key="categories")
        categoryKey.value={"categories":[item for item, in categories.all() ]}
        categoryKey.save()
        all_filters_from_db.cache_clear()
        filters = all_filters_from_db()
    except Exception as e:
        logging.error(str(e))


from book.models import Book
from home.models import Utilities
import logging
from home.views import all_filters_from_db
def languageSchedular():
    try:
        languages = Book.objects.values_list("language").distinct()
        languageKey = Utilities.objects.get(key="languages")
        languageKey.value={"languages":[item for item, in languages.all() ]}
        languageKey.save()
        all_filters_from_db.cache_clear()
        filters = all_filters_from_db()
    except Exception as e:
        logging.error(str(e))
    
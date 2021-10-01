
from book.models import Book
from home.models import Utilities
import logging
from home.views import all_filters_from_db
from redisClient import Client
from datetime import timedelta,datetime
def languageSchedular():
    try:
        languages = Book.objects.values_list("language").filter(language__isnull=False).distinct()
        languageKey = Utilities.objects.get(key="languages")
        languageKey.value={"languages":[item for item, in languages.all() ]}
        languageKey.save()
        Client.setkey("languages",languageKey.value.get("languages"),timedelta(days=1))
    except Exception as e:
        logging.error(str(e))
    
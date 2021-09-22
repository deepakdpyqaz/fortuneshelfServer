
from book.models import Book
from home.models import Utilities
import logging
def languageSchedular():
    try:
        languages = Book.objects.values_list("language").distinct()
        languageKey = Utilities.objects.get(key="languages")
        languageKey.value={"languages":[item for item, in languages.all() ]}
        languageKey.save()
        print("Done language")
    except Exception as e:
        logging.error(str(e))
    
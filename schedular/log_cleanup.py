from django.core.mail import EmailMessage
from django.conf import settings
import datetime
import pytz
import logging
def logCleanup():
    try:
        timzone = pytz.timezone("Asia/Kolkata")
        dt = timzone.localize(datetime.datetime.now())
        message = EmailMessage(
            'Log updates',
            'Log updates for the week',
            settings.DEFAULT_FROM_EMAIL,
            [settings.DEVELOPER_EMAIL,settings.SUPPORT_MAIL]
        )
        message.attach_file("fortuneshelf.log")
        message.send()
        with open("fortuneshelf.log","w") as f:
            pass
    except Exception as e:
        logging.error(str(e))
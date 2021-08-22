import threading
from threading import Thread
from django.conf import settings
from django.core.mail import send_mail
class EmailThread(threading.Thread):
    def __init__(self, subject, html_content, recipient_list):
        self.subject = subject
        self.recipient_list = recipient_list
        self.html_content = html_content
        threading.Thread.__init__(self)

    def run (self):
        send_mail(self.subject,self.html_content, settings.DEFAULT_FROM_EMAIL, self.recipient_list)

def send_html_mail(subject, html_content, recipient_list):
    EmailThread(subject, html_content.get("message"), recipient_list).start()
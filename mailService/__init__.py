import threading
from threading import Thread
from django.conf import settings
from django.core.mail import send_mail
from django.utils.html import strip_tags
from django.template.loader import render_to_string



class EmailThread(threading.Thread):
    def __init__(self, subject,plain_message, html_message, recipient_list):
        self.subject = subject
        self.recipient_list = recipient_list
        self.plain_message = plain_message
        self.html_message = html_message
        threading.Thread.__init__(self)

    def run (self):
        send_mail(self.subject,self.plain_message, settings.DEFAULT_FROM_EMAIL, self.recipient_list,html_message=self.html_message)

def send_html_mail(subject, message, recipient_list):
    html_message = render_to_string(message["template"],message["data"])
    plain_message = strip_tags(html_message)
    EmailThread(subject, plain_message,html_message, recipient_list).start()
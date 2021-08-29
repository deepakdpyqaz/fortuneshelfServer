import threading
from threading import Thread
from django.conf import settings
from django.core.mail import send_mail
from django.utils.html import strip_tags
from django.template.loader import render_to_string
import boto3



class EmailThread(threading.Thread):
    def __init__(self, subject,plain_message, html_message, recipient_list):
        self.subject = subject
        self.recipient_list = recipient_list
        self.plain_message = plain_message
        self.html_message = html_message
        threading.Thread.__init__(self)

    def run (self):
        send_mail(self.subject,self.plain_message, settings.DEFAULT_FROM_EMAIL, self.recipient_list,html_message=self.html_message)

class SmsThread(threading.Thread):
    def __init__(self,subject,message,recipient):
        self.subject=subject
        self.message=message
        self.recipient = recipient
        threading.Thread.__init__(self)

    def run(self):
        client = boto3.client('sns',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_KEY,
            region_name=settings.REGION_NAME
        )
        response = client.publish(
            PhoneNumber=self.recipient,
            Message = self.message,
            Subject = self.subject
        )

def send_html_mail(subject, message, recipient_list):
    html_message = render_to_string(message["template"],message["data"])
    plain_message = strip_tags(html_message)
    EmailThread(subject, plain_message,html_message, recipient_list).start()

def message_generator(key,params):
    messages = {
        "Account Verification": "Welcome to FortuneShelf. Use OTP {} to verify your account".format(params.get("otp",None)),  
        "Verification":"Use OTP {} to verify your account".format(params["otp"]),
        "Reset Password":"We have recieved the request to reset your password. Use OTP {} to reset your password. If you have not made this request then contact enquiry@fortuneshelf.com".format(params.get("otp",None)),
        "Order":"Your order with order ID {} for Rs. {} is placed successfully. Track Your order using {}".format(params.get("orderId"),params.get("amount"),params.get("url"))
    }
    return messages.get(key,"")

def send_sms(subject,message,recipient_list):
    message = message_generator(message['type'], message['params'])
    for recipient in recipient_list:
        recipient="+91"+recipient
        SmsThread(subject, message, recipient).start()
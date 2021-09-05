from order.models import Order
import requests
from django.conf import settings
from book.views import books_by_ids
import threading
from threading import Thread

url = "https://ship.nimbuspost.com/api/orders/create"

class NimbusCreateOrderThread(threading.Thread):
    def __init__(self, order,books):
        self.order = order
        self.books=books
        threading.Thread.__init__(self)

    def run (self):
        products={}
        for id,bk in enumerate(self.books):
            products[f"products[{id}][name]"]=bk.get("title")
            products[f"products[{id}][qty]"]=bk.get("qty")
            products[f"products[{id}][price]"]=bk.get("price")
            payload={
                "order_number":str(self.order.orderId),
                "payment_method": "COD" if self.order.paymentMode=="C" else "prepaid",
                "amount":int(self.order.amount),
                "fname":str(self.order.first_name),
                "lname":str(self.order.last_name),
                "address":str(self.order.address),
                "phone":int(self.order.mobile),
                "city":str(self.order.city),
                "state":str(self.order.state),
                "country":"India",
                "pincode":int(self.order.pincode)
            }
            payload.update(products)
            headers = {
            'NP-API-KEY': settings.NP_API_KEY
            }
            response = requests.request("POST", url, headers=headers, data=payload)
            r = response.json()
            if r["status"]:
                self.order.trackingId=r["data"]
                self.order.save()
                print(self.order.trackingId)
            else:
                print("Error in code")


def create_order(order,books):
    NimbusCreateOrderThread(order, books).start()

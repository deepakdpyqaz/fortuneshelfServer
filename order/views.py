from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from order.models import Order, OrderStatus
import uuid
from book.views import books_by_ids
from mailService import send_html_mail
from order.serializers import OrderSerializer

# Create your views here.

@api_view(["PUT"])
def make_order(request):
    try:
        name = request.data["name"]
        mobile = request.data["mobile"]
        email = request.data["email"]
        pincode = request.data["pincode"]
        state = request.data["state"]
        city = request.data["city"]
        address = request.data["address"]
        district = request.data["district"]
        amount = request.data["amount"]
        paymentMode = request.data["paymentMode"]
        delivery_charges = request.data["delivery_charges"]
        details = request.data["details"]
        order = Order(orderId=uuid.uuid4().hex,name=name,mobile=mobile,email=email,paymentMode=paymentMode,pincode=pincode,state=state,city=city,address=address,district=district,amount=amount,delivery_charges=delivery_charges,details=details)
        order.save()
        books = books_by_ids(details.keys())
        orderItems = {}
        for bk in books:
            bk["qty"] = details[str(bk["book_id"])]
        totalAmount = float(amount)+float(delivery_charges)
        send_html_mail("Order Confirmation",{"template":"mail/order.html","data":{"name":name,"amount":float(amount),"totalAmount":totalAmount,"order_id":order.orderId,"deliveryCharges":float(delivery_charges),"orderDetails":books}} , [email])
        return Response({"status":"success","orderId":order.orderId},status=200)
    except Exception as e:
        return Response({"status":"fail","message":"Order not placed"},status=500)

@api_view(["get"])
def track_order(request):
    orderId = request.query_params.get("orderId")
    if not orderId:
        return Response({"status":"fail","message":"Invalid request"},status=402)
    order = Order.objects.filter(orderId=orderId)
    if not order:
        return Response({"status":"fail","message":"No order found"},status=400)
    serializer = OrderSerializer(order.first())
    response = serializer.data
    response['status'] = OrderStatus(serializer.data['status']).name
    return Response(response,status=200)

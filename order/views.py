from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from order.models import Order, OrderStatus
import uuid
from book.views import books_by_ids, manageStock
from mailService import send_html_mail
from order.serializers import OrderSerializer
import time
from user.views import verify_user, get_user

# Create your views here.

@api_view(["PUT"])
def make_order(request):
    try:
        first_name = request.data["first_name"]
        last_name = request.data["last_name"]
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

        
        order = Order(first_name=first_name,last_name=last_name,mobile=mobile,email=email,paymentMode=paymentMode,pincode=pincode,state=state,city=city,address=address,district=district,amount=amount,delivery_charges=delivery_charges,details=details)
        if "authorization" in request.headers:
            op_status,user = get_user(request.headers.get("authorization",""))
            if op_status:
                order.userId=user
        order.save()
        op_status,op_res = manageStock(details)
        if not op_status:
            return Response(op_res,400)
        books = op_res["data"]
        orderItems = {}
        for bk in books:
            bk["qty"] = details[str(bk["book_id"])]
        totalAmount = float(amount)+float(delivery_charges)
        send_html_mail("Order Confirmation",{"template":"mail/order.html","data":{"name":first_name+" "+last_name,"amount":float(amount),"totalAmount":totalAmount,"order_id":order.orderId,"deliveryCharges":float(delivery_charges),"orderDetails":books}} , [email])
        return Response({"status":"success","orderId":order.orderId},status=200)
    except Exception as e:
        print(e)
        return Response({"status":"fail","message":"Order not placed"},status=500)

@api_view(["get"])
def track_order(request):
    orderId = request.query_params.get("orderId")
    if not orderId:
        return Response({"status":"fail","message":"Invalid request"},status=400)
    order = Order.objects.filter(id=Order.getId(orderId))
    if not order:
        return Response({"status":"fail","message":"No order found"},status=400)
    serializer = OrderSerializer(order.first())
    response = serializer.data
    response['status'] = OrderStatus(serializer.data['status']).name
    books = books_by_ids(response['details'].keys())
    for bk in books:
        bk['qty'] = response['details'][str(bk["book_id"])]
    response['details'] = books
    return Response(response,status=200)

@api_view(["get"])
@verify_user
def get_orders(request):
    orders = Order.objects.filter(userId=request.user).order_by("-date")
    serializer = OrderSerializer(orders,many=True)
    response=[]
    for order in serializer.data:
        order['status'] = OrderStatus(order['status']).name
        order['orderId'] = int(order['id'])+Order.START
        response.append(order)
    
    return Response(response,status=200)
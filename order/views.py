from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from order.models import Order, OrderStatus, Coupon
import uuid
from book.views import books_by_ids, manageStock
from mailService import send_html_mail, send_sms
from order.serializers import OrderSerializer, CouponSerializer
import time
from user.views import verify_user, get_user
from manager.views import verify_manager
import datetime
import pytz
from nimbus.create_order import create_order
from payment.models import Payment,PaymentStatus
from user.serializers import UserSerializer
from django.db.models import Q
import math
import logging
from home.views import getDeliveryChargeFromDb, getCodChargeFromDb
# Create your views here.
timezone = pytz.timezone("Asia/Kolkata")


def calculateCODCharge(amount):
    codCharges = getCodChargeFromDb()
    for charge in codCharges:
        if amount>=charge.get("min") and amount<charge.get("max"):
            return charge.get("price")
    return 50
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
        cod_charges = request.data.get("cod_charges",0)
        paymentMode = request.data["paymentMode"]
        delivery_charges = request.data["delivery_charges"]
        details = request.data["details"]
        couponId = request.data["couponId"]
        if couponId:
            coupon = Coupon.objects.filter(id=couponId)
            if not coupon:
                return Response({"status":"fail","message":"Coupon not valid"},status=400)
            coupon = coupon.first()
            coupon.usage=coupon.usage+1
            coupon.save()
        else:
            coupon = None
        order = Order(first_name=first_name,last_name=last_name,mobile=mobile,email=email,paymentMode=paymentMode,pincode=pincode,state=state,city=city,address=address,district=district,amount=amount,delivery_charges=delivery_charges,details=details,coupon=coupon)
        if "authorization" in request.headers:
            op_status,user = get_user(request.headers.get("authorization",""))
            if op_status:
                order.userId=user
        op_status,op_res = manageStock(details)
        if not op_status:
            return Response(op_res,400)
        books = op_res["data"]
        orderItems = {}
        server_amount = 0
        server_weight = 0
        for bk in books:
            bk["qty"] = details[str(bk["book_id"])]
            server_amount+= int(bk["qty"])*math.ceil((bk["price"]-(bk["discount"]*bk["price"])/100))
            server_weight+=int(bk["qty"])*bk["weight"]*bk["delivery_factor"]
        
        server_total_amount = float(server_amount)+float(math.ceil(server_weight/1000)*getDeliveryChargeFromDb())
        totalAmount = float(amount)+float(delivery_charges)+float(cod_charges)
        if paymentMode=='C' and order.userId:
            codCharges = calculateCODCharge(server_amount)
            order.cod_charges = codCharges
            server_total_amount+=codCharges
        else:
            order.cod_charges = 0
        if abs(totalAmount-server_total_amount)>0.001:
            return Response({"status":"fail","message":"Cart not updated"},status=409)
        if coupon:
            order.discount = math.floor(totalAmount*(coupon.discount)/100)
        else:
            order.discount=0
        order.save()
        totalAmount=totalAmount-order.discount
        if paymentMode=='C' and order.userId:
            create_order(order,books)
            trackingUrl = f"https://fortuneshelf.com/trackorder/?orderId={order.orderId}"
            send_html_mail("Order Confirmation",{"template":"mail/order.html","data":{"name":first_name+" "+last_name,"amount":float(amount),"totalAmount":totalAmount,"discount":order.discount,"order_id":order.orderId,"deliveryCharges":float(delivery_charges),"codCharges":float(cod_charges),"orderDetails":books,"url":trackingUrl}} , [email])
            send_sms(
                "Order Confirmation",
                {"type": "Order", "params": {"name":first_name+" "+last_name,"orderId": order.orderId,"amount":totalAmount,"url":trackingUrl}},
                [mobile],
            )
            return Response({"status":"success","orderId":order.orderId},status=200)
        else:
            payment = Payment(order=order,transactionId=None,status=PaymentStatus.pending.value)
            payment.save()
            return Response({"status":"success","orderId":order.orderId},status=200)
    except Exception as e:
        logging.error(str(e))
        return Response({"status":"fail","message":"Order not placed"},status=500)

@api_view(["get"])
def track_order(request):
    try:
        orderId = request.query_params.get("orderId")
        if not orderId:
            return Response({"status":"fail","message":"Invalid request"},status=400)
        order = Order.objects.filter(id=Order.getId(orderId))
        if not order:
            return Response({"status":"fail","message":"No order found"},status=400)
        order = order.first()
        if order.paymentMode=="O":
            payment = order.payment.first()
            if payment.status!=PaymentStatus.success.value:
                return Response({"status":"fail","message":"No order found"},status=400)
        serializer = OrderSerializer(order)
        response = serializer.data
        response['status'] = OrderStatus(serializer.data['status']).name
        books = books_by_ids(response['details'].keys())
        for bk in books:
            bk['qty'] = response['details'][str(bk["book_id"])]
        response['details'] = books
        return Response(response,status=200)
    except Exception as e:
        logging.error(str(e))
        return Response({"status":"fail","message":"Internal Server Error"},status=500)


@api_view(["get"])
@verify_user
def get_orders(request):
    try:
        orders = Order.objects.filter(Q(userId=request.user),Q(payment=None)|Q(Q(paymentMode='O')&Q(payment__status=PaymentStatus.success.value))).order_by("-date")
        serializer = OrderSerializer(orders,many=True)
        response=[]
        for order in serializer.data:
            order['status'] = OrderStatus(order['status']).name
            order['orderId'] = int(order['id'])+Order.START
            response.append(order)
        
        return Response(response,status=200)
    except Exception as e:
        logging.error(e)
        return Response({"status":"fail","message":"Internal Server Error"},status=500)



@api_view(["get"])
@verify_manager("orders")
def get_all_orders(request):
    try:
        start_date = request.query_params.get("start",None)
        end_date = request.query_params.get("end",None)
        if not start_date or not end_date:
            return Response({"status":"fail","message":"Invalid request"},status=400)
        start_date = timezone.localize(datetime.datetime.strptime(start_date.split("T")[0],"%Y-%m-%d"))
        end_date = timezone.localize(datetime.datetime.strptime(end_date.split("T")[0],"%Y-%m-%d"))+datetime.timedelta(days=1)
        orders = Order.objects.filter(date__gte=start_date,date__lte=end_date).order_by("-date")
        response=[]
        for order in orders:
            paymentStatus="NA"
            if order.payment:
                if order.payment.first():
                    paymentStatus=PaymentStatus(order.payment.first().status).name
            response.append({
                "orderId":order.orderId,
                "email":order.email,
                "mobile":order.mobile,
                "status":OrderStatus(order.status).name,
                "paymentMethod":"COD" if order.paymentMode=="C" else "Online",
                "weight":order.weight,
                "amount":order.amount+order.delivery_charges-order.discount+order.cod_charges,
                "paymentStatus":paymentStatus,
                "address":order.address
            })
        
        return Response({"count":len(response),"data":response},status=200)
    except Exception as e:
        logging.error(str(e))
        return Response({"status":"fail","message":"Internal Server Error"},status=500)

@api_view(["post"])
@verify_manager("orders")
def updateOrderStatus(request,orderId):
    try:
        status = request.data.get("status",None)
        courier_name = request.data.get("courier_name",None)
        courier_url = request.data.get("courier_url",None)
        courier_tracking_id = request.data.get("courier_tracking_id",None)
        message = request.data.get("message",None)
        if status==None:
            return Response({"status":"fail","message":"Invalid request"},status=400)
        order = Order.objects.filter(id=Order.getId(orderId))
        if not order:
            return Response({"status":"fail","message":"Order not found"},status=404)
        order = order.first()
        if order.payment:
            payment = order.payment.first()
            if payment and payment.status !=PaymentStatus.success.value and status!=OrderStatus.failed.value:
                return Response({"status":"fail","message":"Cannot update status if payment is not done"},status=400)
        order.status=status
        order.courier_name = courier_name
        order.courier_url = courier_url
        order.courier_tracking_id = courier_tracking_id
        if message and len(message):
            send_html_mail("Order Update", {"template":"mail/order_status.html","data":{"orderId":order.orderId,"message":message}}, [order.email])
            send_sms("Order Update",{"type":"Order Update","params":{"message":message}},[order.mobile])
        order.save()
        return Response({"status":"successfull"},status=200)
    except Exception as e:
        logging.error(str(e))
        return Response({"status":"fail","message":"Internal server error"},status=500)

@api_view(["GET"])
@verify_manager("orders")
def get_order_details(request,orderId):
    try:
        order = Order.objects.filter(id=Order.getId(orderId))
        if not order:
            return Response({"status":"fail","message":"Order not found"},status=404)
        
        order = order.first()
        serializer = OrderSerializer(order)
        response = serializer.data
        books = books_by_ids(order.details.keys(),True,False)
    
        if order.payment:
            payment = order.payment.first()
            if payment:
                response["transactionId"]=payment.transactionId
                response["paymentStatus"]=PaymentStatus(payment.status).name
                response["error"]=payment.error
                response["mode"]=payment.mode
        response["books"] = [{"bookId":item.bookId,"title":item.title,"language":item.language} for item in books]
        return Response(response,status=200)
    except Exception as e:
        logging.error(str(e))
        return Response({"status":"fail","message":"Internal Server Error"},status=500)

@api_view(["GET"])
@verify_manager("coupon")
def get_all_coupons(request):
    try:
        coupons = Coupon.objects.all().order_by("-generated_on")
        serializer = CouponSerializer(coupons,many=True)
        return Response(serializer.data,status=200)
    except Exception as e:
        logging.error(str(e))
        return Response({"status":"fail","message":"Internal Server Error"},status=500)

@api_view(["POST"])
@verify_manager("coupon")
def create_coupon(request):
    try:
        coupon = request.data.get("coupon",None)
        discount = request.data.get("discount",None)
        if not coupon or not discount:
            return Response({"status":"fail","message":"Invalid request"},status=400)
        discount_coupon = Coupon(coupon=coupon,usage=0,discount=discount,isValid=True)
        discount_coupon.save()
        return Response({"status":"success"},status=201)
    except Exception as e:
        logging.error(str(e))
        return Response({"status":'fail',"message":"Internal server Error"},status=500)

@api_view(["delete"])
@verify_manager("coupon")
def delete_coupon(request,couponId):
    try:
        coupon = Coupon.objects.filter(id=couponId)
        if not coupon:
            return Response({"status":"fail","message":"Coupon not found"},status=404)
        coupon.delete()
        return Response({"status":"success"},status=201)
    except Exception as e:
        logging.error(str(e))
        return Response({"status":'fail',"message":"Internal server Error"},status=500)
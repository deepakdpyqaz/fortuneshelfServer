from django.shortcuts import render, redirect
from rest_framework.decorators import api_view
from django.conf import settings
from order.models import Order, OrderStatus, Coupon
from payment.models import PaymentStatus, Payment
from django.views.decorators.csrf import csrf_exempt
from rest_framework.response import Response
from django.conf import settings
from hashlib import sha512
from nimbus.create_order import create_order
from mailService import send_html_mail, send_sms
from book.views import books_by_ids, manageStock
from manager.views import verify_manager
import pytz
import datetime


timezone = pytz.timezone("Asia/Kolkata")

# Create your views here.
PRODUCTINFO = "FortuneShelf Books"

class PAYU:
    REQUIRED_HASH_SEQUENCE = 'txnid|amount|productinfo|firstname|email'
    OPTIONAL_HASH_SEQUENCE ='udf1|udf2|udf3|udf4|udf5|udf6|udf7|udf8|udf9|udf10'
    salt = settings.MERCHANT_SALT
    key = settings.MERCHANT_KEY

    @classmethod
    def generate_hash(self, data):
        assert type(data) == dict, 'arg `data` must be a dict'
        hash_str = f'{self.key}|'
        try:
            data['amount'] = str(int(data['amount']))
            hash_str += '|'.join([data[k] for k in self.REQUIRED_HASH_SEQUENCE.split('|')])
        except KeyError as e:
            raise Exception(f'key {e} missing from arg data')
        
        hash_str += '|'
        hash_str += '|'.join([data.get(k, '') for k in self.OPTIONAL_HASH_SEQUENCE.split('|')])
        hash_str += f'|{self.salt}'
        
        hashh = hash_str.encode('utf-8')
        return sha512(hashh).hexdigest().lower()
    @classmethod
    def check_hash(self, data):
        assert type(data) == dict, 'arg `data` must be a dict'

        required_hash_keys = reversed(self.REQUIRED_HASH_SEQUENCE.split('|'))
        optional_hash_keys = reversed(self.OPTIONAL_HASH_SEQUENCE.split('|'))
        hash_str = ''
        
        
        try:
            hash_str += self.salt
            hash_str += f'|{data["status"]}|'
            hash_str += '|'.join([data.get(key, '') for key in optional_hash_keys])

            hash_str += '|'

            hash_str += '|'.join([str(data[key]) for key in required_hash_keys])
        except KeyError as e:
            raise Exception(f'key {e} missing from arg data')
        
        hash_str += f'|{self.key}'
        
        hashh = hash_str.encode('utf-8')
        return (sha512(hashh).hexdigest().lower() == data.get('hash'))

@api_view(["GET"])
def getMerchantKey(request):
    orderId=request.query_params.get("orderId",None)
    mobile = request.query_params.get("mobile",None)
    email = request.query_params.get("email",None)

    if not orderId or not mobile or not email:
        return Response({"status":"fail","message":"Invalid Request"},status=400)
    order = Order.objects.filter(id=Order.getId(orderId))
    if not order:
        return Response({"status":"fail","message":"Order not found"},status=400)
    order = order.first()
    hash_dict={"firstname":order.first_name,"txnid":orderId,"amount":order.amount+order.delivery_charges-order.discount,"email":email,"productinfo":PRODUCTINFO}
    hash = PAYU.generate_hash(hash_dict)
    if order.payment.first().status == PaymentStatus.pending.value and order.mobile == mobile and order.email==email:
        return Response({"status":"success","merchant_key":settings.MERCHANT_KEY,"merchant_salt":settings.MERCHANT_SALT,"curl":settings.CURL,"furl":settings.FURL,"surl":settings.SURL,"hash":hash,"productinfo":PRODUCTINFO})
    return Response({"status":"fail","message":"Invalid Request"},status=400)


@api_view(["GET"])
def getPaymentStatus(request,orderId):
    if not orderId:
        return Response({"status":"fail","message":"OrderId not provided"},status=404)
    order = Order.objects.filter(id=Order.getId(orderId))
    if not order:
        return Response({"status":"fail","message":"Order not found"},status=404)
    order = order.first()
    payment = order.payment.first()
    payment_status = payment.status if payment!=None else PaymentStatus.success.value
    return Response({"payment_status":PaymentStatus(payment_status).name},status=200)

@csrf_exempt
def success(request):
    res = {}
    for i in request.POST.keys():
        res[i]=request.POST[i]
    if PAYU.check_hash(res):
        order = Order.objects.filter(id=Order.getId(res.get("txnid")))
        if not order:
            return redirect(settings.RURL)
        order=order.first()
        payment = order.payment.first()
        payment.status = PaymentStatus.success.value
        payment.transactionId = res.get("mihpayid")
        payment.mode = res.get("mode")
        payment.save()
        op_status,op_res = manageStock(order.details,False)
        if not op_status:
            return Response(op_res,400)
        order.save()
        books = op_res["data"]
        orderItems = {}
        for bk in books:
            bk["qty"] = order.details[str(bk["book_id"])]
        totalAmount = float(order.amount)+float(order.delivery_charges)-float(order.discount)
        create_order(order,books)
        trackingUrl = f"https://fortuneshelf.com/trackorder/?orderId={order.orderId}"
        send_html_mail("Order Confirmation",{"template":"mail/order.html","data":{"name":order.first_name+" "+order.last_name,"amount":float(order.amount),"discount":float(order.discount),"codCharges":0,"totalAmount":totalAmount,"order_id":order.orderId,"deliveryCharges":float(order.delivery_charges),"orderDetails":books,"url":trackingUrl}} , [order.email])
        send_sms(
            "Order Confirmation",
            {"type": "Order", "params": {"name":order.first_name+" "+order.last_name,"orderId": order.orderId,"amount":totalAmount,"url":trackingUrl}},
            [order.mobile],
        )

        return redirect(settings.RURL+f"?orderId={order.orderId}")
    else:
        return redirect(settings.RURL+f"?orderId={order.orderId}")
@csrf_exempt
def fail(request):
    res = {}
    for i in request.POST.keys():
        res[i]=request.POST[i]
    if PAYU.check_hash(res):
        order = Order.objects.filter(id=Order.getId(res.get("txnid")))
        if not order:
            return redirect(settings.RURL+f"?orderId={order.orderId}")
        order=order.first()
        payment = order.payment.first()
        payment.status = PaymentStatus.fail.value
        payment.error = res.get("error_message")
        order.status=OrderStatus.failed.value
        order.save()
        payment.save()
    return redirect(settings.RURL+f"?orderId={order.orderId}")

@csrf_exempt
def cancel(request):
    res = {}
    for i in request.POST.keys():
        res[i]=request.POST[i]
    if PAYU.check_hash(res):
        order = Order.objects.filter(id=Order.getId(res.get("txnid")))
        if not order:
            return redirect(settings.RURL+f"?orderId={order.orderId}")
        order=order.first()
        payment = order.payment.first()
        payment.status = PaymentStatus.fail.value
        payment.error = res.get("error_message")
        order.status=OrderStatus.failed.value
        order.save()
        payment.save()
    return redirect(settings.RURL+f"?orderId={order.orderId}")


@api_view(["get"])
@verify_manager("payment")
def get_all_payments(request):
    start_date = request.query_params.get("start",None)
    end_date = request.query_params.get("end",None)
    if not start_date or not end_date:
        return Response({"status":"fail","message":"Invalid request"},status=400)
    start_date = timezone.localize(datetime.datetime.strptime(start_date.split("T")[0],"%Y-%m-%d"))
    end_date = timezone.localize(datetime.datetime.strptime(end_date.split("T")[0],"%Y-%m-%d")+datetime.timedelta(days=1))
    payments = Payment.objects.filter(date__gte=start_date,date__lte=end_date).order_by("-date")
    response=[]
    for payment in payments:    
       response.append({
           "transactionId":payment.transactionId,
           "orderId":payment.order.orderId,
           "status":PaymentStatus(payment.status).name,
           "date":payment.date,
           "error":payment.error,
           "mode":payment.mode
       })
    
    return Response({"count":len(response),"data":response},status=200)

@api_view(["get"])
def applyCoupon(request,coupon):
    discountCoupon = Coupon.objects.filter(coupon=coupon)
    if not discountCoupon:
        return Response({"status":"fail","message":"Coupon Not Found"},status=200)
    discountCoupon = discountCoupon.first()
    if not discountCoupon.isValid:
        return Response({"status":"fail","message":"Coupon Expired"},status=200)
    return Response({"status":"success","coupon":discountCoupon.coupon,"discount":discountCoupon.discount,"coupon_id":discountCoupon.id},status=200)

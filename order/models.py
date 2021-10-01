from django.db import models
import enum
from user.models import User
# Create your models here.
class OrderStatus(enum.Enum):
    pending = 0
    packed = 1
    shipped = 2
    delivered = 3
    failed = -1

class Coupon(models.Model):
    coupon = models.CharField(max_length=50)
    discount = models.FloatField(default=0.0)
    isValid = models.BooleanField(default=True)
    usage = models.IntegerField()
    generated_on = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.coupon
class Order(models.Model):
    userId = models.ForeignKey(User,null=True,blank=True,on_delete = models.SET_NULL)
    coupon = models.ForeignKey(Coupon,null=True,blank=True,on_delete=models.SET_NULL)
    first_name=models.CharField(max_length=50)
    last_name=models.CharField(max_length=50,default="")
    mobile = models.CharField(max_length=15)
    email = models.CharField(max_length=40)
    address = models.TextField()
    pincode = models.CharField(max_length=8)
    city = models.CharField(max_length=30)
    state = models.CharField(max_length=30)
    district = models.CharField(max_length=30)
    amount = models.FloatField()
    delivery_charges = models.FloatField()
    cod_charges = models.FloatField(default=0,null=True,blank=True)
    details = models.JSONField()
    trackingId = models.CharField(max_length=30,null=True)
    courier_url = models.CharField(max_length=100,null=True,blank=True,default=None)
    courier_tracking_id = models.CharField(max_length=50,null=True,blank=True,default=None)
    courier_name=models.CharField(max_length=100,null=True,blank=True,default=None)
    discount = models.FloatField(default=0,blank=True,null=True)
    status = models.IntegerField(default=OrderStatus.pending.value)
    date = models.DateTimeField(auto_now_add=True, blank=True)
    weight = models.FloatField(default=0,null=True,blank=True)
    dimension = models.CharField(default="",null=True,blank=True,max_length=15)
    PAYMENTMODE = (
        ("C","COD"),
        ("O","ONLINE")
    )
    paymentMode = models.CharField(max_length=10,choices=PAYMENTMODE )
    def __str__(self):
        return str(self.orderId) 

    START = 100000
        
    @property
    def orderId(self):
        return self.START+self.id
    
    @classmethod
    def getId(self,orderId):
        return int(orderId) - self.START

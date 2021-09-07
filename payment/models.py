from django.db import models
from order.models import Order
import enum
# Create your models here.
class PaymentStatus(enum.Enum):
    success=1
    fail=-1
    pending=0
class Payment(models.Model):
    order = models.ForeignKey(Order,on_delete=models.SET_NULL,null=True,related_name="payment")
    transactionId = models.CharField(max_length=30,null=True)
    status = models.IntegerField(default=PaymentStatus.pending.value)
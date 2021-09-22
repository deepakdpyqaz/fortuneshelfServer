from order.models import Order,OrderStatus
from payment.models import Payment,PaymentStatus
import datetime
import pytz
import logging
def orderCleanup():
    try:
        timezone = pytz.timezone("Asia/Kolkata")
        dt = timezone.localize(datetime.datetime.now()-datetime.timedelta(days=2))
        payments = Payment.objects.filter(date__lte=dt,status=PaymentStatus.pending.value)
        for payment in payments:
            order = payment.order
            order.status = OrderStatus.failed.value
            payment.status = PaymentStatus.fail.value
            payment.error = "Payment not completed properly"
            order.save()
            payment.save()
    except Exception as e:
        logging.error(str(e))
    
from django.db import models
import bcrypt

# Create your models here.
class User(models.Model):
    mobile = models.CharField(max_length=15,unique=True,null=True)
    email = models.CharField(max_length=50,unique=True,null=True)
    name = models.CharField(max_length=50)
    _password = models.CharField(max_length=50,null=True)
    age = models.IntegerField(null=True)
    GENDER=[
        ('M',"Male"),
        ('F',"Female"),
        ('O',"other")
    ]
    gender = models.CharField(max_length=2,choices=GENDER,null=True)
    token = models.CharField(max_length=20,null=True)
    created_on = models.DateTimeField(null=True)
    otp = models.IntegerField(null=True)
    @property
    def password(self):
        return self._password

    @password.setter
    def password(self,passwd):
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(passwd, salt)
        self._password = password
    
    def verify_password(self,passwd):
        return bcrypt.checkpw(passwd,self._password)

class UserUnverified(models.Model):
    mobile = models.CharField(max_length=15,unique=True,null=True)
    email = models.CharField(max_length=50,unique=True,null=True)
    name = models.CharField(max_length=50)
    age = models.IntegerField(null=True)
    GENDER=[
        ('M',"Male"),
        ('F',"Female"),
        ('O',"other")
    ]
    gender = models.CharField(max_length=2,choices=GENDER,null=True)
    emailOtp = models.IntegerField(null=True)
    mobileOtp = models.IntegerField(null=True)

class BillingProfile(models.Model):
    userId = models.ForeignKey(User, on_delete=models.CASCADE,related_name="billing_profile")
    address = models.TextField()
    pincode = models.CharField(max_length=8)
    city = models.CharField(max_length=30)
    state = models.CharField(max_length=30)
    country = models.CharField(max_length=30)
    district = models.CharField(max_length=30)


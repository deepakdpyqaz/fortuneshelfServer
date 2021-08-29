from django.db import models
import bcrypt

# Create your models here.
class User(models.Model):
    mobile = models.CharField(max_length=15,unique=True,null=True)
    email = models.CharField(max_length=50,unique=True,null=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    _password = models.CharField(max_length=100,null=True)
    age = models.IntegerField(null=True)
    GENDER=[
        ('M',"Male"),
        ('F',"Female"),
        ('O',"other")
    ]
    gender = models.CharField(max_length=2,choices=GENDER,null=True)
    otp = models.IntegerField(null=True)
    generated_on = models.DateTimeField(auto_now_add=True)
    @property
    def password(self):
        return self._password

    @password.setter
    def password(self,passwd):
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(passwd.encode("utf-8"), salt)
        self._password = hashed.decode('utf-8')
    
    def verify_password(self,passwd):
        return bcrypt.checkpw(passwd.encode("utf-8"),self._password.encode("utf-8"))

    def __str__(self):
        return self.first_name + " "+ self.last_name

class UserUnverified(models.Model):
    mobile = models.CharField(max_length=15,null=True)
    email = models.CharField(max_length=50,null=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    age = models.IntegerField(null=True)
    GENDER=[
        ('M',"Male"),
        ('F',"Female"),
        ('O',"other")
    ]
    gender = models.CharField(max_length=2,choices=GENDER,null=True)
    emailOtp = models.IntegerField(null=True)
    mobileOtp = models.IntegerField(null=True)
    otpGenTime=models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.first_name + " "+ self.last_name


class BillingProfile(models.Model):
    userId = models.ForeignKey(User, on_delete=models.CASCADE,related_name="billing_profile")
    title = models.CharField(default="default",max_length=100)
    address = models.TextField()
    pincode = models.CharField(max_length=8)
    city = models.CharField(max_length=30)
    state = models.CharField(max_length=30)
    country = models.CharField(max_length=30)
    district = models.CharField(max_length=30)

    def __str__(self):
        return self.userId.first_name + " "+self.userId.last_name

class Token(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=100)
    created_on = models.DateTimeField()

    def __str__(self):
        return self.user.first_name+" "+self.user.last_name
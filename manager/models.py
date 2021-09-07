from django.db import models
import bcrypt
# Create your models here.
class Manager(models.Model):
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    email = models.EmailField(max_length=100)
    _password = models.CharField(max_length=100,null=True)
    mobile = models.CharField(max_length=12)
    books = models.BooleanField(default=False)
    orders = models.BooleanField(default=False)
    users = models.BooleanField(default=False)
    payment=models.BooleanField(default=False)
    otp = models.IntegerField(default=0)
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
        return f"{self.first_name} {self.last_name}"

class AdminToken(models.Model):
    manager = models.ForeignKey(Manager,on_delete=models.CASCADE)
    token = models.CharField(max_length=100)
    created_on = models.DateTimeField(auto_now_add=True)
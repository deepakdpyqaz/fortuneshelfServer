from django.db import models

# Create your models here.
class Utilities(models.Model):
    key=models.CharField(max_length=30,db_index=True,unique=True)
    value = models.JSONField()

    def __str__(self):
        return self.key

class Pincode(models.Model):
    pincode = models.CharField(max_length=6)
    state=models.CharField(max_length=30)
    district=models.CharField(max_length=40)

class Banner(models.Model):
    picture = models.ImageField(upload_to="banner")
    title = models.CharField(max_length=20,null=True,blank=True)
    link = models.CharField(max_length=200,null=True,blank=True)

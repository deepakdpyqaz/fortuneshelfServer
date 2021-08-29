from django.db import models

# Create your models here.
class Book(models.Model):
    START = 1000000
    title=models.CharField(max_length=100,db_index=True)
    price = models.IntegerField(db_index=True)
    author = models.CharField(max_length=100)
    language = models.CharField(max_length=20,db_index=True)
    discount = models.FloatField(default=0.0)
    dimension = models.CharField(max_length=20)
    weight = models.FloatField()
    description = models.TextField(default="")
    max_stock = models.IntegerField(default=10000)
    picture = models.ImageField(upload_to="books",default="default.jpg")
    delivery_factor = models.FloatField(default=1)
    view_count = models.BigIntegerField(default=0,db_index=True)
    def __str__(self):
        return self.title
    
    @property
    def bookId(self):
        return self.START+self.id
    
    @classmethod
    def getId(self,bookId):
        return int(bookId) - self.START
    
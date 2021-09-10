from django.db import models

# Create your models here.
class Book(models.Model):
    START = 1000000
    title=models.CharField(max_length=100,db_index=True)
    price = models.IntegerField(db_index=True)
    author = models.CharField(max_length=100,default="A.C. Bhaktivedanta Swami Srila Prabhupada")
    language = models.CharField(max_length=20,db_index=True)
    discount = models.FloatField(default=0.0)
    weight = models.FloatField()
    description = models.TextField(default="")
    max_stock = models.IntegerField(default=10000)
    picture = models.ImageField(upload_to="books",default="default.jpg")
    delivery_factor = models.FloatField(default=1)
    view_count = models.BigIntegerField(default=0,db_index=True)
    category = models.CharField(null=True,blank=True,max_length=30,db_index=True,default=None)
    length = models.IntegerField(default=0,null=True,blank=True)
    breadth = models.IntegerField(default=0,null=True,blank=True)
    height = models.IntegerField(default=0,null=True,blank=True)
    def __str__(self):
        return self.title
    
    @property
    def bookId(self):
        return self.START+self.id
    
    @classmethod
    def getId(self,bookId):
        return int(bookId) - self.START

    @property
    def dimension(self):
        return f"{self.length} x {self.breadth} x {self.height} cm"
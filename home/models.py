from django.db import models

# Create your models here.
class Utilities(models.Model):
    key=models.CharField(max_length=30,db_index=True,unique=True)
    value = models.JSONField()

    def __str__(self):
        return self.key
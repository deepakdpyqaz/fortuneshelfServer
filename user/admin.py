from django.contrib import admin
from . models import User, BillingProfile, UserUnverified
# Register your models here.

admin.site.register(User)
admin.site.register(UserUnverified)
admin.site.register(BillingProfile)


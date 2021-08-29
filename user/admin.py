from django.contrib import admin
from . models import User, BillingProfile, UserUnverified,Token
# Register your models here.

admin.site.register(User)
admin.site.register(UserUnverified)
admin.site.register(BillingProfile)
admin.site.register(Token)


from django.contrib import admin
from manager.models import Manager, AdminToken
# Register your models here.
admin.site.register(Manager)
admin.site.register(AdminToken)

from django.contrib import admin

from .models import Farmer, Inquiry, Product

admin.site.register(Farmer)
admin.site.register(Product)
admin.site.register(Inquiry)
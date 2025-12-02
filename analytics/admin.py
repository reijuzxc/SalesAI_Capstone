from django.contrib import admin
from .models import SalesRecord, CustomerFeedback

# This tells the Admin panel to show these tables
admin.site.register(SalesRecord)
admin.site.register(CustomerFeedback)

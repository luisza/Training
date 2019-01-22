from django.contrib import admin

from filterviews.models import Invoice

class InvoiceAdmin(admin.ModelAdmin):
    date_hierarchy = 'start_date'

admin.site.register(Invoice, InvoiceAdmin)
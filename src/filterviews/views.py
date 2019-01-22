from django.shortcuts import render

# Create your views here.
from django.views.generic import ListView

from filterviews.models import Invoice


class InvoiceView(ListView):
    model = Invoice
    date_hierarchy = 'start_date'

    def get_queryset(self):
        query = super(InvoiceView, self).get_queryset()
        fday = self.request.GET.get(self.date_hierarchy+"__day", '')
        if fday:
            filters = {
                self.date_hierarchy + "__day": fday
            }
            query = query.filter(**filters)

        return query

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(InvoiceView, self).get_context_data()
        context['date_hierarchy'] = self.date_hierarchy
        return context
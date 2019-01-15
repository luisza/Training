from django.contrib import admin

# Register your models here.

from .models import Elector, District, Canton, Province

class ElectorAdmin(admin.ModelAdmin):
    list_display = ('fullName', 'get_gender_display', 'get_canton_info')
    search_fields = ('codelec__canton__province__name', )


    def get_canton_info(self, instance):
        return instance.codelec.canton

admin.site.register(Elector, ElectorAdmin)
admin.site.register([District, Canton, Province])

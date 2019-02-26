from django.db.models import Sum, F
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Elector, District, Canton, Province




@receiver([post_save, post_delete], sender=Elector)
def update_stats_handler(sender, instance, **kwargs):
    print("Update signals ", sender, instance)

    if instance.gender == 1:
        District.objects.filter(codelec=instance.codelec.codelec).update(stats_male=F('stats_male') + 1,
                                                          stats_total=F('stats_total') + 1)

        Canton.objects.filter(pk=instance.canton.code).update(stats_male=F('stats_male') + 1,
                                                       stats_total=F('stats_total') + 1)

        Province.objects.filter(pk=instance.canton.province.code).update(stats_male=F('stats_male') + 1,
                                                                  stats_total=F('stats_total') + 1)
    else:
        District.objects.filter(pk=instance.codelec.codelec).update(stats_female=F('stats_female') + 1,
                                                          stats_total=F('stats_total') + 1)

        Canton.objects.filter(pk=instance.canton.code).update(stats_female=F('stats_female') + 1,
                                                       stats_total=F('stats_total') + 1)

        Province.objects.filter(pk=instance.canton.province.code).update(stats_female=F('stats_female') + 1,
                                                                  stats_total=F('stats_total') + 1)

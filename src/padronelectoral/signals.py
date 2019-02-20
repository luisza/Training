from django.db.models import Sum
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Elector, District, Canton


def update_district(district):
    elector_list = Elector.objects.filter(codelec=district.pk)
    district.stats_female = elector_list.filter(gender=2).count()
    district.stats_male = elector_list.filter(gender=1).count()
    district.stats_total = district.stats_female + district.stats_male
    district.save()

def update_canton(canton):
    dist_list = District.objects.all()
    canton.stats_male = dist_list.filter(canton=canton.pk).aggregate(Sum('stats_male'))
    canton.stats_female = dist_list.filter(canton=canton.pk).aggregate(Sum('stats_female'))
    canton.stats_total = dist_list.filter(canton=canton.pk).aggregate(Sum('stats_total'))

    canton.save()

def update_province(province):
    cant_list = Canton.objects.all()
    province.stats_male = cant_list.filter(province = province.pk).aggregate(Sum('stats_male'))
    province.stats_female = cant_list.filter(province=province.pk).aggregate(Sum('stats_female'))
    province.stats_total = cant_list.filter(province=province.pk).aggregate(Sum('stats_total'))

    province.save()

@receiver([post_save, post_delete], sender=Elector)
def update_stats_handler(sender, instance,  **kwargs):
    print("Update signals ", sender, instance)
    update_district(instance.codelec)
    update_canton(instance.canton)
    update_province(instance.canton.province)
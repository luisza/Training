from django.db.models import Sum, F
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

    dist_list = District.objects.filter(canton=canton.pk)
    dist_list = dist_list.annotate(t_men=Sum(F('stats_male')),
                                   t_women=Sum(F('stats_female')),
                                   t_electors=Sum(F('stats_total')))
    for d in dist_list:
        canton.stats_total = d.t_electors
        canton.stats_female = d.t_women
        canton.stats_male = d.t_men
        canton.save()


def update_province(province):
    cant_list = Canton.objects.filter(province=province.pk)
    cant_list = cant_list.annotate(t_men=Sum('stats_male'),
                                   t_women=Sum(F('stats_female')),
                                   t_electors=Sum(F('stats_total')))
    for c in cant_list:
        province.stats_male = c.t_men
        province.stats_female = c.t_women
        province.stats_total = c.t_electors
        province.save()


@receiver([post_save, post_delete], sender=Elector)
def update_stats_handler(sender, instance,  **kwargs):
    print("Update signals ", sender, instance)
    update_district(instance.codelec)
    update_canton(instance.canton)
    update_province(instance.canton.province)
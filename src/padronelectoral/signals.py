from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Elector, District

def update_district(district):
    elector_list = Elector.objects.filter(codelec=district.pk)
    district.stats_female = elector_list.filter(gender=2).count()
    district.stats_male = elector_list.filter(gender=1).count()
    district.stats_total = district.stats_female + district.stats_male
    district.save()


@receiver([post_save, post_delete], sender=Elector)
def update_district_handler(sender, instance,  **kwargs):
    print("Update signals ", sender, instance)
    update_district(instance.codelec)

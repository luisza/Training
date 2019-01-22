from django.db import models
from django.core.validators import MaxValueValidator
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _


# Create your models here.
class Province(models.Model):
    code = models.SmallIntegerField(primary_key=True)
    name = models.CharField(max_length=10)
    stats_female = models.IntegerField(default=-1, null=True)
    stats_male = models.IntegerField(default=-1, null=True)
    stats_total = models.IntegerField(default=-1, null=True)

    def __str__(self):
        return self.name

class Canton(models.Model):
    code = models.SmallIntegerField(primary_key=True)
    name = models.CharField(max_length=30)
    stats_female = models.IntegerField(default=-1, null=True)
    stats_male = models.IntegerField(default=-1, null=True)
    stats_total = models.IntegerField(default=-1, null=True)
    province = models.ForeignKey(Province, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class District(models.Model):
    codelec=models.PositiveIntegerField(primary_key=True, validators=[MaxValueValidator(999999999)])
    name = models.CharField(max_length=34)
    canton=models.ForeignKey(Canton, on_delete=models.CASCADE)

    stats_female = models.IntegerField(default=-1)
    stats_male = models.IntegerField(default=-1)
    stats_total = models.IntegerField(default=-1)

    def __str__(self):
        return self.name

class Elector(models.Model):
    GENDER = (
        (1, 'Male'),
        (2, "Female"))
    idCard = models.PositiveIntegerField(primary_key=True, validators=[MaxValueValidator(999999999)])
    codelec = models.ForeignKey(District, on_delete=models.CASCADE)
    gender = models.SmallIntegerField(choices=GENDER, verbose_name=_("Genero"),
                                      help_text=_("Hombre o mujer"))
    cad_date = models.DateField()
    board = models.IntegerField(validators=[MaxValueValidator(999999)])
    #not sure that this can be "" by default.
    fullName = models.CharField(max_length=100)

    def __str__(self):
        return self.fullName

    @property
    def get_gender_display(self):
        from django.templatetags.static import static
        if self.gender == 1:
            return mark_safe('<img src="%s" />'%( static('/man-user.png')))
        else:
            return "Female dd"
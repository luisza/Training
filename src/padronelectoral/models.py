from django.db import models
from django.core.validators import MaxValueValidator
# Create your models here.
class Province(models.Model):
    code = models.SmallIntegerField(default=1)
    name = models.CharField(max_length=10)

    def __str__(self):
        return self.name

class Canton(models.Model):
    code = models.SmallIntegerField(default=1)
    name = models.CharField(max_length=30)
    province = models.ForeignKey(Province,on_delete=models.CASCADE, default=1)

    def __str__(self):
        return self.name


class District(models.Model):
    codelec=models.PositiveIntegerField(primary_key=True, validators=[MaxValueValidator(999999999)])
    name = models.CharField(max_length=34)
    canton=models.ForeignKey(Canton, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

class Elector(models.Model):
    idCard = models.PositiveIntegerField(primary_key=True, validators=[MaxValueValidator(999999999)])
    codelec = models.ForeignKey(District, on_delete=models.CASCADE)
    gender = models.SmallIntegerField()
    cad_date = models.DateField()
    board = models.IntegerField(validators=[MaxValueValidator(999999)])
    #not sure that this can be "" by default.
    fullName = models.CharField(max_length=100)

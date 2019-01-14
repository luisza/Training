from django.db import models
from django.core.validators import MaxValueValidator
# Create your models here.
class Province(models.Model):
    id = models.SmallIntegerField(primary_key=True)
    name = models.CharField(max_length=10)

class Canton(models.Model):
    name = models.CharField(max_length=20)
    idProvince = models.ForeignKey(Province,on_delete=models.CASCADE, default=1)


class District(models.Model):
    id = models.SmallIntegerField(primary_key=True)
    codelec=models.PositiveIntegerField(validators=[MaxValueValidator(999999)])
    name = models.CharField(max_length=34)
    canton=models.ForeignKey(Canton, on_delete=models.CASCADE)

class Elector(models.Model):
    idCard = models.PositiveIntegerField(primary_key=True, validators=[MaxValueValidator(999999999)])
    codelec = models.ForeignKey(District, on_delete=models.CASCADE)
    gender = models.SmallIntegerField()
    cad_date = models.DateField()
    board = models.IntegerField(validators=[MaxValueValidator(999999)])
    #not sure that this can be "" by default.
    fullName = models.CharField(max_length=100,default="")
    name = models.CharField(max_length=30)
    lastname1 = models.CharField(max_length=26)
    lastname2 = models.CharField(max_length=26)
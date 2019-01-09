from django.db import models
from django.core.validators import MaxValueValidator
# Create your models here.
class Provincia(models.Model):
    nombreProvincia= models.CharField(max_length=10)

class Canton(models.Model):
    nombreCanton=models.CharField(max_length=20)
    provincia=models.ForeignKey(Provincia,on_delete=models.CASCADE)

class Distrito(models.Model):
    codelec=models.PositiveIntegerField(primary_key=True,validators=[MaxValueValidator(999999)])
    nombreProvincia = models.CharField(max_length=34)
    canton=models.ForeignKey(Canton, on_delete=models.CASCADE)

class Elector(models.Model):
    cedula=models.PositiveIntegerField(primary_key=True, validators=[MaxValueValidator(999999999)])
    codelec=models.ForeignKey(Distrito, on_delete=models.CASCADE)
    sexo=models.SmallIntegerField()
    fecha_cad=models.DateField()
    junta=models.IntegerField(validators=[MaxValueValidator(999999)])
    nombre=models.CharField(max_length=30)
    apellido1=models.CharField(max_length=26)
    apellido2 = models.CharField(max_length=26)
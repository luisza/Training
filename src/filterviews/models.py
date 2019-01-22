from django.db import models

# Create your models here.


class Invoice(models.Model):
    start_date = models.DateField()
    name = models.CharField(max_length=140)

    def __str__(self):
        return self.name
# Generated by Django 2.1.5 on 2019-01-14 18:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('padronelectoral', '0005_auto_20190114_1803'),
    ]

    operations = [
        migrations.AlterField(
            model_name='district',
            name='codelec',
            field=models.CharField(max_length=6),
        ),
    ]

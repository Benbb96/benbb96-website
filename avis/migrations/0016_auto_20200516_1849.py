# Generated by Django 2.2.12 on 2020-05-16 16:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('avis', '0015_auto_20191028_1454'),
    ]

    operations = [
        migrations.AlterField(
            model_name='categorieproduit',
            name='slug',
            field=models.SlugField(unique=True),
        ),
    ]

# Generated by Django 2.2.12 on 2020-06-09 23:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('my_spot', '0006_auto_20200516_1849'),
    ]

    operations = [
        migrations.AlterField(
            model_name='spotphoto',
            name='photo',
            field=models.TextField(default='placeholder.jpg', help_text="Vous pouvez également renseigner l'URL d'une image sur internet.", verbose_name='url photo'),
        ),
    ]

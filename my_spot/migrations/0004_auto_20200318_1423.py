# Generated by Django 2.2.9 on 2020-03-18 13:23

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('my_spot', '0003_spotgroup_date_creation'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='spotgroup',
            options={'ordering': ('nom',)},
        ),
    ]
# Generated by Django 2.2.6 on 2019-12-25 21:54

from django.db import migrations, models
from django.utils import timezone


def set_date_validation(apps, schema_editor):
    Lien = apps.get_model("music", "Lien")
    db_alias = schema_editor.connection.alias
    Lien.objects.using(db_alias).update(date_validation=timezone.now())


class Migration(migrations.Migration):

    dependencies = [
        ('music', '0007_auto_20191028_1454'),
    ]

    operations = [
        migrations.AddField(
            model_name='lien',
            name='date_validation',
            field=models.DateTimeField(blank=True, null=True, verbose_name='date de validation'),
        ),
        migrations.RunPython(set_date_validation)
    ]

# Generated by Django 2.1.1 on 2018-09-28 09:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tracker', '0002_tracker_slug'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='track',
            options={'ordering': ('-datetime',)},
        ),
        migrations.AlterField(
            model_name='track',
            name='commentaire',
            field=models.CharField(blank=True, help_text='Un texte pour donner une explication sur ce track.', max_length=255),
        ),
    ]
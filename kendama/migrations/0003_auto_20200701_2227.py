# Generated by Django 2.2.13 on 2020-07-01 20:27

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('kendama', '0002_historicalcomboplayer_historicaltrickplayer'),
    ]

    operations = [
        migrations.AlterField(
            model_name='trickplayer',
            name='trick',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='trick_players', to='kendama.KendamaTrick'),
        ),
    ]

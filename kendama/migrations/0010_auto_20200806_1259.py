# Generated by Django 2.2.13 on 2020-08-06 10:59

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('kendama', '0009_auto_20200723_1616'),
    ]

    operations = [
        migrations.AlterField(
            model_name='combotrick',
            name='trick',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='combo_tricks', to='kendama.KendamaTrick'),
        ),
        migrations.AlterField(
            model_name='laddercombo',
            name='combo',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ladder_combos', to='kendama.Combo'),
        ),
        migrations.AlterField(
            model_name='trickplayer',
            name='trick',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='trick_players', to='kendama.KendamaTrick'),
        ),
    ]

# Generated by Django 2.1.11 on 2019-08-16 06:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0006_auto_20190731_1549'),
        ('tracker', '0004_auto_20181010_1343'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='tracker',
            options={'ordering': ['order']},
        ),
        migrations.AddField(
            model_name='tracker',
            name='order',
            field=models.PositiveIntegerField(db_index=True, default=0, editable=False),
        ),
        migrations.AlterUniqueTogether(
            name='tracker',
            unique_together={('createur', 'nom')},
        ),
    ]

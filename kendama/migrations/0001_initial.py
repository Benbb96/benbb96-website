# Generated by Django 2.2.12 on 2020-06-21 12:06

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('base', '0008_projet_position'),
    ]

    operations = [
        migrations.CreateModel(
            name='Combo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('slug', models.SlugField(max_length=100, unique=True)),
                ('description', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='date création')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='date mise à jour')),
                ('difficulty', models.PositiveSmallIntegerField(choices=[(1, 'Débutant'), (2, 'Intermédiaire'), (3, 'Avancé')], verbose_name='difficulté')),
                ('tutorial_video_link', models.URLField(blank=True, verbose_name='lien vidéo tutoriel')),
                ('creator', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='base.Profil', verbose_name='créateur')),
            ],
            options={
                'ordering': ('-created_at',),
            },
        ),
        migrations.CreateModel(
            name='KendamaTrick',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('slug', models.SlugField(max_length=100, unique=True)),
                ('description', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='date création')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='date mise à jour')),
                ('difficulty', models.PositiveSmallIntegerField(choices=[(1, 'Débutant'), (2, 'Intermédiaire'), (3, 'Avancé')], verbose_name='difficulté')),
                ('tutorial_video_link', models.URLField(blank=True, verbose_name='lien vidéo tutoriel')),
                ('creator', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='base.Profil', verbose_name='créateur')),
            ],
            options={
                'verbose_name': 'trick de Kendama',
                'verbose_name_plural': 'tricks de Kendama',
                'ordering': ('-created_at',),
            },
        ),
        migrations.CreateModel(
            name='Kendama',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('photo', models.TextField(default='placeholder.jpg', help_text="Vous pouvez également renseigner l'URL d'une image sur internet.", verbose_name='url photo')),
                ('name', models.CharField(max_length=100)),
                ('slug', models.SlugField(max_length=100, unique=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='date de création')),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='kendamas', to='base.Profil', verbose_name='possesseur')),
            ],
            options={
                'ordering': ('-created_at',),
            },
        ),
        migrations.CreateModel(
            name='ComboTrick',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order', models.PositiveSmallIntegerField(db_index=True, default=0, verbose_name='ordre')),
                ('combo', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='combo_tricks', to='kendama.Combo')),
                ('trick', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='combo_tricks', to='kendama.KendamaTrick')),
            ],
        ),
        migrations.AddField(
            model_name='combo',
            name='tricks',
            field=models.ManyToManyField(related_name='combos', through='kendama.ComboTrick', to='kendama.KendamaTrick'),
        ),
        migrations.CreateModel(
            name='TrickPlayer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('frequency', models.PositiveSmallIntegerField(choices=[(1, 'Impossible'), (2, 'Seulement une fois'), (3, 'Rarement'), (4, 'Parfois'), (5, 'Généralement'), (6, 'Tout le temps')], default=1, verbose_name='fréquence de réussite')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='date création')),
                ('player', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='base.Profil', verbose_name='joueur')),
                ('trick', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='trick_player', to='kendama.KendamaTrick')),
            ],
            options={
                'verbose_name': 'trick de joueur',
                'verbose_name_plural': 'tricks de joueur',
                'unique_together': {('trick', 'player')},
            },
        ),
        migrations.CreateModel(
            name='ComboPlayer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('frequency', models.PositiveSmallIntegerField(choices=[(1, 'Impossible'), (2, 'Seulement une fois'), (3, 'Rarement'), (4, 'Parfois'), (5, 'Généralement'), (6, 'Tout le temps')], default=1, verbose_name='fréquence de réussite')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='date création')),
                ('combo', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='combo_players', to='kendama.Combo')),
                ('player', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='base.Profil', verbose_name='joueur')),
            ],
            options={
                'verbose_name': 'combo de joueur',
                'verbose_name_plural': 'combos de joueur',
                'unique_together': {('combo', 'player')},
            },
        ),
    ]

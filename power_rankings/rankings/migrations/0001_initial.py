# Generated by Django 4.2.3 on 2023-10-21 19:46

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Team',
            fields=[
                ('team_id', models.IntegerField(default=0, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=200)),
                ('rank', models.IntegerField(default=-1)),
            ],
        ),
        migrations.CreateModel(
            name='Player',
            fields=[
                ('name', models.CharField(max_length=200)),
                ('player_id', models.IntegerField(default=0, primary_key=True, serialize=False)),
                ('team', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='rankings.team')),
            ],
        ),
    ]

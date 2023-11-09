# Generated by Django 4.2.3 on 2023-10-21 23:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rankings', '0002_rename_name_player_player_name_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='team',
            old_name='rank',
            new_name='skill',
        ),
        migrations.RemoveField(
            model_name='player',
            name='player_name',
        ),
        migrations.RemoveField(
            model_name='team',
            name='team_name',
        ),
        migrations.AddField(
            model_name='player',
            name='first_name',
            field=models.CharField(default=None, max_length=200),
        ),
        migrations.AddField(
            model_name='player',
            name='handle',
            field=models.CharField(default=None, max_length=200),
        ),
        migrations.AddField(
            model_name='player',
            name='last_name',
            field=models.CharField(default=None, max_length=200),
        ),
        migrations.AddField(
            model_name='team',
            name='level',
            field=models.CharField(default=None, max_length=200),
        ),
        migrations.AddField(
            model_name='team',
            name='name',
            field=models.CharField(default=None, max_length=200),
        ),
        migrations.AlterField(
            model_name='player',
            name='player_id',
            field=models.IntegerField(default=None, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='team',
            name='team_id',
            field=models.IntegerField(default=None, primary_key=True, serialize=False),
        ),
    ]
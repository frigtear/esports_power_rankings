# Generated by Django 4.2.3 on 2023-10-22 20:03

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('rankings', '0010_rename_assists_player_scaledkd_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='player',
            old_name='scaledLosses',
            new_name='scaledWR',
        ),
        migrations.RemoveField(
            model_name='player',
            name='scaledWins',
        ),
    ]

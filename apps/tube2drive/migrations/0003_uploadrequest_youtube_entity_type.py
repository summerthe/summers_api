# Generated by Django 3.2.13 on 2022-07-23 13:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tube2drive', '0002_uploadrequest_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='uploadrequest',
            name='youtube_entity_type',
            field=models.CharField(blank=True, choices=[('PLAYLIST', 'PLAYLIST'), ('CHANNEL', 'CHANNEL'), ('VIDEO', 'VIDEO')], default='PLAYLIST', max_length=8),
        ),
    ]
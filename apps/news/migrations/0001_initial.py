# Generated by Django 3.2.13 on 2022-06-11 17:54

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('guid', models.UUIDField(default=uuid.uuid4, editable=False, verbose_name='guid')),
                ('title', models.CharField(max_length=255, unique=True)),
                ('slug', models.SlugField(editable=False, unique=True)),
            ],
            options={
                'verbose_name': 'Category',
                'verbose_name_plural': 'Categories',
                'ordering': ['-updated_at'],
            },
        ),
        migrations.CreateModel(
            name='Newsletter',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('guid', models.UUIDField(default=uuid.uuid4, editable=False, verbose_name='guid')),
            ],
            options={
                'verbose_name': 'Newsletter',
                'verbose_name_plural': 'Newsletters',
                'ordering': ['-updated_at'],
            },
        ),
        migrations.CreateModel(
            name='SavedArticle',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('guid', models.UUIDField(default=uuid.uuid4, editable=False, verbose_name='guid')),
                ('article', models.JSONField()),
            ],
            options={
                'verbose_name': 'Newsletter',
                'verbose_name_plural': 'Newsletters',
                'ordering': ['-updated_at'],
            },
        ),
    ]

# Generated by Django 3.2.23 on 2024-01-12 12:35

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main_page', '0004_auto_20240112_1333'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pig',
            name='owner',
            field=models.ManyToManyField(blank=True, null=True, related_name='PIG_owner', to=settings.AUTH_USER_MODEL),
        ),
    ]
# Generated by Django 3.2.23 on 2024-01-12 18:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main_page', '0006_alter_pig_owner'),
    ]

    operations = [
        migrations.AddField(
            model_name='breeding',
            name='nickname',
            field=models.CharField(default='', max_length=100),
        ),
    ]
# Generated by Django 3.2.23 on 2024-01-12 21:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main_page', '0008_alter_breeding_nickname'),
    ]

    operations = [
        migrations.AlterField(
            model_name='breeding',
            name='nickname',
            field=models.CharField(max_length=100),
        ),
    ]

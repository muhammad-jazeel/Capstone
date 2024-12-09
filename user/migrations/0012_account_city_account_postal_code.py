# Generated by Django 5.1.1 on 2024-12-08 07:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0011_account_address_account_profile_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='account',
            name='city',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='account',
            name='postal_code',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
    ]
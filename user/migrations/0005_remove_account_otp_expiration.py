# Generated by Django 5.1.1 on 2024-12-03 00:17

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0004_account_otp_expiration'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='account',
            name='otp_expiration',
        ),
    ]
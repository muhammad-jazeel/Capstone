# Generated by Django 5.1.1 on 2024-11-22 00:04

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('reservation', '0002_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='reservation',
            name='vendor_service',
        ),
        migrations.RemoveField(
            model_name='timeslot',
            name='vendor_service',
        ),
    ]

# Generated by Django 5.1.1 on 2024-12-08 06:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reservation', '0004_alter_reservation_time_slot_reservation_comments_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='reservation',
            name='car_registration',
            field=models.CharField(max_length=50, null=True),
        ),
    ]

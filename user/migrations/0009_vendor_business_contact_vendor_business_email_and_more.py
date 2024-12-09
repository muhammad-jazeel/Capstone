# Generated by Django 5.1.1 on 2024-12-04 21:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0008_vendor_business_license_vendor_verification_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='vendor',
            name='business_contact',
            field=models.CharField(blank=True, max_length=15, null=True),
        ),
        migrations.AddField(
            model_name='vendor',
            name='business_email',
            field=models.EmailField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='vendor',
            name='description',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='vendor',
            name='address',
            field=models.TextField(blank=True, null=True),
        ),
    ]

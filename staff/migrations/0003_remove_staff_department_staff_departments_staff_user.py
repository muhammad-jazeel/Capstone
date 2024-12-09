# Generated by Django 5.1.1 on 2024-11-18 22:19

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('department', '0002_department_created_by'),
        ('staff', '0002_alter_staff_department_delete_department'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RemoveField(
            model_name='staff',
            name='department',
        ),
        migrations.AddField(
            model_name='staff',
            name='departments',
            field=models.ManyToManyField(related_name='staff', to='department.department'),
        ),
        migrations.AddField(
            model_name='staff',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='staff', to=settings.AUTH_USER_MODEL),
        ),
    ]
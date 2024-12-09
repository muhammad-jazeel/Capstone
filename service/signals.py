from datetime import timedelta, datetime, date
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Service, BookingSlot


@receiver(post_save, sender=Service)
def create_slots(sender, instance, created, **kwargs):
    """
    Generate booking slots whenever a service is created or updated.
    """
    if instance.start_time and instance.end_time and instance.duration_minutes:
        instance.slots.all().delete()

        current_time = instance.start_time
        delta = timedelta(minutes=instance.duration_minutes)

        while current_time < instance.end_time:
            BookingSlot.objects.create(service=instance, slot_time=current_time)
            current_time = (datetime.combine(date.today(), current_time) + delta).time()

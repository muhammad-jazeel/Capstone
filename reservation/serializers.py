# serializers.py
from rest_framework import serializers
from .models import TimeSlot, Reservation

class TimeSlotSerializer(serializers.ModelSerializer):
    class Meta:
        model = TimeSlot
        fields = ['id', 'vendor_service', 'date', 'start_time', 'end_time', 'is_booked', 'created_at', 'updated_at']

class ReservationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reservation
        fields = ['id', 'customer', 'vendor_service', 'time_slot', 'status', 'total_price', 'payment_status', 'created_at', 'updated_at']

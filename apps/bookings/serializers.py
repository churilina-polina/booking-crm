from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers

from .models import Booking, Payment


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ('id', 'booking', 'amount', 'method', 'status', 'paid_at')
        read_only_fields = ('status', 'paid_at')


class BookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = (
            'id', 'client', 'employee', 'service', 'start_time', 'end_time',
            'status', 'comment', 'created_at', 'updated_at',
        )
        read_only_fields = ('client', 'status', 'created_at', 'updated_at', 'end_time')

    def validate(self, attrs):
        service = attrs.get('service') or getattr(self.instance, 'service', None)
        start_time = attrs.get('start_time') or getattr(self.instance, 'start_time', None)
        if service and start_time:
            attrs['end_time'] = start_time + service.duration
        return attrs

    def create(self, validated_data):
        validated_data['client'] = self.context['request'].user
        booking = Booking(**validated_data)
        try:
            booking.full_clean()
        except DjangoValidationError as exc:
            raise serializers.ValidationError(exc.message_dict or exc.messages)
        booking.save()
        return booking

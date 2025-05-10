from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from .models import Room, Reservation, RoomClosure

class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Room
        fields = ('id', 'name', 'price', 'capacity')

class ReservationCreateSerializer(serializers.ModelSerializer):
    rooms = serializers.PrimaryKeyRelatedField(queryset=Room.objects.all(), many=True)
    email = serializers.EmailField(required=False, allow_null=True)
    phone = serializers.CharField(required=False, allow_null=True)

    class Meta:
        model  = Reservation
        fields = (
            'guest_name', 'number_of_guests', 'email', 'phone',
            'rooms', 'payment_method', 'check_in', 'check_out', 'additional_info',
        )

    def validate(self, data):
        ci, co = data['check_in'], data['check_out']
        if ci >= co:
            raise ValidationError('`check_out` must be after `check_in`.')
        if not data.get('email') and not data.get('phone'):
            raise ValidationError('Provide either email or phone.')

        # find unavailable rooms
        reserved = Reservation.objects.filter(
            status='confirmed',
            check_in__lt=co, check_out__gt=ci
        ).values_list('rooms', flat=True)
        closed = RoomClosure.objects.filter(
            start_date__lt=co, end_date__gte=ci
        ).values_list('room_id', flat=True)
        unavailable = set(reserved) | set(closed)

        for room in data['rooms']:
            if room.id in unavailable:
                raise ValidationError(f'Room "{room.name}" not available for {ci} → {co}.')

        total_capacity = sum(r.capacity for r in data['rooms'])
        if data['number_of_guests'] > total_capacity:
            raise ValidationError('Not enough capacity across selected rooms.')

        return data

    @transaction.atomic
    def create(self, validated_data):
        rooms = validated_data.pop('rooms')
        # lock to avoid race‑condition double booking
        Reservation.objects.select_for_update(nowait=False)
        reservation = Reservation.objects.create(**validated_data)
        reservation.rooms.set(rooms)
        return reservation

class ReservationSerializer(serializers.ModelSerializer):
    rooms = RoomSerializer(many=True, read_only=True)

    class Meta:
        model  = Reservation
        fields = (
            'id', 'guest_name', 'number_of_guests',
            'rooms', 'payment_method', 'check_in', 'check_out',
            'status', 'additional_info', 'created_at',
        )
        read_only_fields = ('status', 'created_at')

class RoomClosureSerializer(serializers.ModelSerializer):
    class Meta:
        model  = RoomClosure
        fields = ('id', 'room', 'start_date', 'end_date', 'reason')

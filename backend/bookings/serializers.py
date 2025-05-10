import logging
from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from .models import Room, RoomImage, Reservation, RoomClosure

logger = logging.getLogger(__name__)


class RoomImageSerializer(serializers.ModelSerializer):
    room = serializers.PrimaryKeyRelatedField(queryset=Room.objects.all())

    class Meta:
        model = RoomImage
        fields = ('id', 'room', 'image', 'caption', 'order')


class RoomSerializer(serializers.ModelSerializer):
    images = RoomImageSerializer(many=True, read_only=True)
    amenities = serializers.ListField(
        child=serializers.CharField(),
        read_only=True,
        help_text="List of amenities, e.g., ['wifi','ac','minibar']"
    )

    class Meta:
        model = Room
        fields = (
            'id', 'name', 'description', 'price', 'capacity',
            'size_sqm', 'floor', 'bed_count', 'bed_type', 'view_type',
            'amenities', 'is_active', 'under_maintenance',
            'images', 'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'created_at', 'updated_at')


class ReservationCreateSerializer(serializers.ModelSerializer):
    rooms = serializers.PrimaryKeyRelatedField(queryset=Room.objects.all(), many=True)
    email = serializers.EmailField(required=False, allow_null=True)
    phone = serializers.CharField(required=False, allow_null=True)

    class Meta:
        model = Reservation
        fields = (
            'guest_name', 'number_of_guests', 'email', 'phone',
            'rooms', 'payment_method', 'check_in', 'check_out', 'additional_info'
        )

    def validate(self, data):
        ci, co = data['check_in'], data['check_out']
        logger.debug('Validating reservation: %s → %s for %s', ci, co, data.get('guest_name'))
        if ci >= co:
            logger.warning('Invalid dates: %s ≥ %s', ci, co)
            raise ValidationError('`check_out` must be after `check_in`.')
        if not data.get('email') and not data.get('phone'):
            logger.warning('Missing contact info')
            raise ValidationError('Provide either email or phone.')

        # Check availability
        from .models import Reservation as R, RoomClosure
        reserved = R.objects.filter(
            status='confirmed', check_in__lt=co, check_out__gt=ci
        ).values_list('rooms', flat=True)
        closed = RoomClosure.objects.filter(
            start_date__lt=co, end_date__gte=ci
        ).values_list('room_id', flat=True)
        unavailable = set(reserved) | set(closed)

        for room in data['rooms']:
            if room.id in unavailable:
                logger.info('Room unavailable: %s', room)
                raise ValidationError(f'Room "{room.name}" not available for {ci} → {co}.')

        total_capacity = sum(r.capacity for r in data['rooms'])
        if data['number_of_guests'] > total_capacity:
            logger.info('Capacity exceeded: %s guests, capacity %s', data['number_of_guests'], total_capacity)
            raise ValidationError('Not enough space to fit all people.')

        return data

    @transaction.atomic
    def create(self, validated_data):
        rooms = validated_data.pop('rooms')
        logger.info('Creating reservation for %s', validated_data.get('guest_name'))
        # create without m2m
        res = Reservation.objects.create(**validated_data)
        # attach rooms
        res.rooms.set(rooms)
        # compute total price
        res.total_price = res.get_total_price()
        res.save(update_fields=['total_price'])
        logger.info('Reservation created: %s', res.id)
        return res


class ReservationSerializer(serializers.ModelSerializer):
    rooms = RoomSerializer(many=True, read_only=True)

    class Meta:
        model = Reservation
        fields = (
            'id', 'guest_name', 'number_of_guests', 'rooms', 'payment_method',
            'check_in', 'check_out', 'total_price', 'status', 'additional_info', 'created_at'
        )
        read_only_fields = ('id', 'total_price', 'status', 'created_at')


class RoomClosureSerializer(serializers.ModelSerializer):
    class Meta:
        model = RoomClosure
        fields = ('id', 'room', 'start_date', 'end_date', 'reason')

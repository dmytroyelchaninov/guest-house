import logging
from datetime import datetime
from django.conf import settings
from django.core.mail import send_mail
from django.db import transaction
from django.db.models import Q
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .email_utils import send_reservation_emails, send_cancellation_emails
from .models import Room, Reservation, RoomClosure
from .serializers import (
    RoomSerializer,
    ReservationCreateSerializer,
    ReservationSerializer
)

logger = logging.getLogger(__name__)

@api_view(['GET'])
def available_rooms(request):
    logger.debug('available_rooms called with GET %s', request.GET)
    ci_str = request.GET.get('check_in')
    co_str = request.GET.get('check_out')
    if not ci_str or not co_str:
        logger.warning('Missing check_in or check_out')
        return Response({'detail': 'Provide check_in and check_out.'}, status=400)
    try:
        ci = datetime.fromisoformat(ci_str).date()
        co = datetime.fromisoformat(co_str).date()
    except ValueError:
        logger.error('Invalid date format: %s or %s', ci_str, co_str)
        return Response({'detail': 'Dates must be YYYY-MM-DD.'}, status=400)
    if ci >= co:
        logger.warning('check_out %s not after check_in %s', co, ci)
        return Response({'detail': 'check_out must be after check_in.'}, status=400)

    booked_ids = Reservation.objects.filter(
        status='confirmed', check_in__lt=co, check_out__gt=ci
    ).values_list('rooms', flat=True)
    closed_ids = RoomClosure.objects.filter(
        start_date__lt=co, end_date__gte=ci
    ).values_list('room_id', flat=True)
    unavailable = set(booked_ids) | set(closed_ids)
    logger.debug('Unavailable room ids: %s', unavailable)

    rooms = Room.objects.exclude(id__in=unavailable)
    data = RoomSerializer(rooms, many=True).data
    logger.info('Returning %d available rooms', len(data))
    return Response(data)


@api_view(['GET', 'POST'])
def reservations(request):
    if request.method == 'GET':
        logger.debug('reservations GET with params %s', request.GET)
        key = request.GET.get('email') or request.GET.get('phone')
        if not key:
            logger.warning('Missing email/phone on GET reservations')
            return Response({'detail': 'Provide email or phone.'}, status=400)
        qs = Reservation.objects.filter(
            status='confirmed'
        ).filter(
            Q(email=key) | Q(phone=key)
        )
        data = ReservationSerializer(qs, many=True).data
        logger.info('Found %d reservations for key %s', len(data), key)
        return Response(data)

    # POST / create
    logger.debug('reservations POST with body %s', request.data)
    slz = ReservationCreateSerializer(data=request.data)
    slz.is_valid(raise_exception=True)
    with transaction.atomic():
        reservation = slz.save()
    logger.info('Created reservation id=%s', reservation.id)

    send_reservation_emails(reservation)

    out = ReservationSerializer(reservation).data
    return Response(out, status=201)


@api_view(['POST'])
def cancel_reservation(request, pk):
    logger.debug('cancel_reservation called for id=%s with body %s', pk, request.data)
    key = request.data.get('email') or request.data.get('phone')
    if not key:
        logger.warning('Missing email/phone on cancel')
        return Response({'detail': 'Provide email or phone.'}, status=400)

    try:
        res = Reservation.objects.get(pk=pk, status='confirmed')
    except Reservation.DoesNotExist:
        logger.error('Reservation id=%s not found or not confirmed', pk)
        return Response(status=404)

    if key not in (res.email, res.phone):
        logger.warning('Unauthorized cancel attempt for id=%s with key=%s', pk, key)
        return Response(status=403)

    # mark cancelled
    res.status = 'cancelled'
    res.save(update_fields=['status'])
    logger.info('Reservation id=%s cancelled', pk)

    # send both guest + owner emails
    send_cancellation_emails(res)

    return Response(status=204)


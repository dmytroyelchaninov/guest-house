from datetime import datetime
from django.conf import settings
from django.core.mail import send_mail
from django.db import transaction
from django.db.models import Q
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Room, Reservation, RoomClosure
from .serializers import (
    RoomSerializer, ReservationCreateSerializer, ReservationSerializer
)

@api_view(['GET'])
def available_rooms(request):
    ci_str = request.GET.get('check_in')
    co_str = request.GET.get('check_out')
    if not ci_str or not co_str:
        return Response({'detail': 'Provide check_in and check_out.'}, status=400)
    try:
        ci, co = datetime.fromisoformat(ci_str).date(), datetime.fromisoformat(co_str).date()
    except ValueError:
        return Response({'detail': 'Dates must be YYYY-MM-DD.'}, status=400)
    if ci >= co:
        return Response({'detail': 'check_out must be after check_in.'}, status=400)

    booked_ids = Reservation.objects.filter(status='confirmed', check_in__lt=co, check_out__gt=ci).values_list('rooms', flat=True)
    closed_ids = RoomClosure.objects.filter(start_date__lt=co, end_date__gte=ci).values_list('room_id', flat=True)
    unavailable = set(booked_ids) | set(closed_ids)

    rooms = Room.objects.exclude(id__in=unavailable)
    return Response(RoomSerializer(rooms, many=True).data)

@api_view(['GET', 'POST'])
def reservations(request):
    if request.method == 'GET':
        key = request.GET.get('email') or request.GET.get('phone')
        if not key:
            return Response({'detail': 'Provide email or phone.'}, status=400)
        qs = Reservation.objects.filter(status='confirmed').filter(Q(email=key) | Q(phone=key))
        return Response(ReservationSerializer(qs, many=True).data)

    slz = ReservationCreateSerializer(data=request.data)
    slz.is_valid(raise_exception=True)
    with transaction.atomic():
        reservation = slz.save()

    # email notifications (console backend in dev)
    if reservation.email:
        send_mail(
            'Booking confirmed',
            f'Booking #{reservation.id} confirmed for {reservation.check_in}—{reservation.check_out}.',
            settings.DEFAULT_FROM_EMAIL,
            [reservation.email],
            fail_silently=True,
        )
    send_mail(
        f'New booking #{reservation.id}',
        f'Guest {reservation.guest_name}\nDates {reservation.check_in}—{reservation.check_out}',
        settings.DEFAULT_FROM_EMAIL,
        [settings.DEFAULT_FROM_EMAIL],
        fail_silently=True,
    )

    return Response(ReservationSerializer(reservation).data, status=201)

@api_view(['POST'])
def cancel_reservation(request, pk):
    key = request.data.get('email') or request.data.get('phone')
    if not key:
        return Response({'detail': 'Provide email or phone.'}, status=400)
    try:
        res = Reservation.objects.get(pk=pk, status='confirmed')
    except Reservation.DoesNotExist:
        return Response(status=404)
    if key not in (res.email, res.phone):
        return Response(status=403)

    res.status = 'cancelled'
    res.save(update_fields=['status'])

    if res.email:
        send_mail('Booking cancelled', f'Your booking #{res.id} was cancelled.', settings.DEFAULT_FROM_EMAIL, [res.email], fail_silently=True)
    send_mail(f'Booking #{res.id} cancelled', 'Cancelled by guest', settings.DEFAULT_FROM_EMAIL, [settings.DEFAULT_FROM_EMAIL], fail_silently=True)

    return Response(status=204)

import logging
from django.conf import settings
from django.core import signing, mail
from rest_framework.permissions import BasePermission
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser

from .models import Room, RoomImage, RoomClosure, Reservation
from .serializers import RoomSerializer, RoomClosureSerializer, ReservationSerializer, RoomImageSerializer


TOKEN_SALT  = settings.TOKEN_SALT
COOKIE_NAME = settings.COOKIE_NAME
MAX_AGE     = settings.MAX_AGE


logger = logging.getLogger(__name__)

class HotelAdminPermission(BasePermission):
    def has_permission(self, request, view):
        token = request.COOKIES.get(COOKIE_NAME)
        if not token:
            logger.warning('No admin token in cookies')
            return False
        try:
            data = signing.loads(token, salt=TOKEN_SALT, max_age=MAX_AGE)
            valid = data.get('admin') is True
            logger.debug('Admin permission check: %s', valid)
            return valid
        except signing.BadSignature:
            logger.error('Invalid admin token signature')
            return False


class RoomAdminViewSet(ModelViewSet):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer
    permission_classes = [HotelAdminPermission]


class RoomImageAdminViewSet(ModelViewSet):
    queryset         = RoomImage.objects.all()
    serializer_class = RoomImageSerializer
    permission_classes = [HotelAdminPermission]
    parser_classes     = [MultiPartParser, FormParser]

    def initial(self, request, *args, **kwargs):
        logger.debug('RoomImageAdminViewSet called, data=%s', request.data)
        return super().initial(request, *args, **kwargs)

class ClosureAdminViewSet(ModelViewSet):
    """
    GET, POST, PUT/PATCH, DELETE on RoomClosure.
    DELETE will 'open' the room for that date range.
    """
    queryset = RoomClosure.objects.all()
    serializer_class = RoomClosureSerializer
    permission_classes = [HotelAdminPermission]

    def destroy(self, request, *args, **kwargs):
        logger.info('Deleting closure id=%s', kwargs.get('pk'))
        return super().destroy(request, *args, **kwargs)

class ReservationAdminViewSet(ModelViewSet):
    """
    Admin can list all reservations and archive them.
    """
    queryset = Reservation.objects.all()
    serializer_class = ReservationSerializer
    permission_classes = [HotelAdminPermission]

    @action(detail=True, methods=['post'])
    def archive(self, request, pk=None):
        """
        POST /api/admin/reservations/{pk}/archive/
        """
        res = self.get_object()
        res.status = 'archived'
        res.save(update_fields=['status'])
        logger.info('Archived reservation id=%s', pk)

        # send thank-you email to guest
        if res.email:
            subject = "Thank you for staying with us!"
            body = (
                f"Dear {res.guest_name},\n\n"
                "Thank you for choosing our hotel. We hope you had a wonderful stay!\n\n"
                "We look forward to welcoming you back soon.\n\n"
                "Best regards,\nThe Team"
            )
            mail.send_mail(
                subject,
                body,
                settings.DEFAULT_FROM_EMAIL,
                [res.email],
                fail_silently=True
            )
            logger.debug('Sent archive email to %s', res.email)

        return Response(self.get_serializer(res).data)
    

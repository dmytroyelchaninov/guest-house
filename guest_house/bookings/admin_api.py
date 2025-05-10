from django.conf import settings
from django.core import signing
from rest_framework.permissions import BasePermission
from rest_framework.viewsets import ModelViewSet
from rest_framework.routers import DefaultRouter

from .models import Room, RoomClosure
from .serializers import RoomSerializer, RoomClosureSerializer

TOKEN_SALT = settings.TOKEN_SALT
COOKIE_NAME = settings.COOKIE_NAME
MAX_AGE     = settings.MAX_AGE

class HotelAdminPermission(BasePermission):
    def has_permission(self, request, view):
        token = request.COOKIES.get(COOKIE_NAME)
        if not token:
            return False
        try:
            data = signing.loads(token, salt=TOKEN_SALT, max_age=MAX_AGE)
            return data.get('admin') is True
        except signing.BadSignature:
            return False

class RoomAdminViewSet(ModelViewSet):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer
    permission_classes = [HotelAdminPermission]

class ClosureAdminViewSet(ModelViewSet):
    queryset = RoomClosure.objects.all()
    serializer_class = RoomClosureSerializer
    permission_classes = [HotelAdminPermission]

# router exposed as module‑level urlpatterns for include()
router = DefaultRouter()
router.register('rooms', RoomAdminViewSet, basename='admin-rooms')
router.register('closures', ClosureAdminViewSet, basename='admin-closures')
urlpatterns = router.urls

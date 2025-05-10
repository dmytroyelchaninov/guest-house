from django.contrib import admin
from django.urls import path, include

from rest_framework.routers import DefaultRouter

from bookings.views import available_rooms, reservations, cancel_reservation
from bookings.views_admin import admin_login, admin_logout
from bookings.admin_api import RoomAdminViewSet, ClosureAdminViewSet, ReservationAdminViewSet, RoomImageAdminViewSet


urlpatterns = [
    path('admin/', admin.site.urls),  # optional built‑in admin (auth‑based)

    # Admin login/logout by key
    path('api/admin/login/',  admin_login,  name='hotel-admin-login'),
    path('api/admin/logout/', admin_logout, name='hotel-admin-logout'),

    # public API
    path('api/rooms/available/',           available_rooms,       name='rooms-available'),

    path('api/reservations/',              reservations,          name='reservations'),
    path('api/reservations/<int:pk>/cancel/', cancel_reservation, name='reservation-cancel'),
]

#  Mini admin API
router = DefaultRouter()
router.register('api/admin/rooms',      RoomAdminViewSet,        basename='admin-rooms')
router.register('api/admin/room-images', RoomImageAdminViewSet, basename='admin-room-images')
router.register('api/admin/closures',   ClosureAdminViewSet,     basename='admin-closures')
router.register('api/admin/reservations', ReservationAdminViewSet, basename='admin-reservations')

urlpatterns += router.urls


#  ├─ api/
#  │   ├─ admin/
#  │   │   ├─ login/        → bookings.views_admin.admin_login
#  │   │   ├─ logout/       → bookings.views_admin.admin_logout
#  │   │   ├─ rooms/        → bookings.admin_api.RoomAdminViewSet
#  │   │   ├─ closures/     → bookings.admin_api.ClosureAdminViewSet
#  │   │   └─ reservations/ → bookings.admin_api.ReservationAdminViewSet
#  │   ├─ rooms/
#  │   │   └─ available/    → bookings.views.available_rooms
#  │   └─ reservations/
#  │       ├─    GET        → bookings.views.reservations
#  │       └─ <int:pk>/cancel/ → bookings.views.cancel_reservation
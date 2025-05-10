from django.contrib import admin
from django.urls import path, include

from bookings.views import available_rooms, reservations, cancel_reservation
from bookings.views_admin import admin_login, admin_logout

urlpatterns = [
    path('admin/', admin.site.urls),  # optional built‑in admin (auth‑based)

    # token‑based mini admin API
    path('api/admin/login/',  admin_login,  name='hotel-admin-login'),
    path('api/admin/logout/', admin_logout, name='hotel-admin-logout'),
    path('api/admin/',        include('bookings.admin_api')),

    # public API
    path('api/rooms/available/',           available_rooms,       name='rooms-available'),
    path('api/reservations/',              reservations,          name='reservations'),
    path('api/reservations/<int:pk>/cancel/', cancel_reservation, name='reservation-cancel'),
]


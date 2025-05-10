from django.contrib import admin
from .models import Room, Reservation, RoomClosure

@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'capacity')
    search_fields = ('name',)
    ordering = ('-price',)

@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ('guest_name','number_of_guests','email','phone','check_in','check_out','status')
    filter_horizontal = ('rooms',)
    date_hierarchy = 'check_in'

@admin.register(RoomClosure)
class RoomClosureAdmin(admin.ModelAdmin):
    list_display = ('room','start_date','end_date','reason')
    list_filter  = ('room',)

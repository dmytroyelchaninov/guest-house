from django.db import models
from django.utils import timezone

class Room(models.Model):
    name     = models.CharField(max_length=80, unique=True)
    price    = models.DecimalField(max_digits=8, decimal_places=2)
    capacity = models.PositiveIntegerField(default=2)

    def __str__(self):
        return self.name

class Reservation(models.Model):
    STATUS_CHOICES = [
        ('confirmed', 'Confirmed'),
        ('archived',  'Archived'),
        ('cancelled', 'Cancelled'),
    ]

    guest_name       = models.CharField(max_length=120)
    number_of_guests = models.PositiveIntegerField(default=1)
    email            = models.EmailField(blank=True, null=True)
    phone            = models.CharField(max_length=40, blank=True, null=True)
    rooms            = models.ManyToManyField(Room, related_name='reservations')
    payment_method   = models.CharField(max_length=20, choices=[('cash','Cash'),('bank_transfer','Bank Transfer')], default='cash')
    check_in         = models.DateField()
    check_out        = models.DateField()
    status           = models.CharField(max_length=20, choices=STATUS_CHOICES, default='confirmed')
    created_at       = models.DateTimeField(default=timezone.now)
    additional_info  = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.guest_name} ({self.check_in}\u2192{self.check_out})"

class RoomClosure(models.Model):
    room       = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='closures')
    start_date = models.DateField()
    end_date   = models.DateField()
    reason     = models.CharField(max_length=255, blank=True)

    class Meta:
        constraints = [
            models.CheckConstraint(check=models.Q(end_date__gte=models.F('start_date')), name='closure_end_after_start')
        ]
        ordering = ['start_date']

    def __str__(self):
        return f"{self.room.name} closed {self.start_date}\u2192{self.end_date}"


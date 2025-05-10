import logging
from django.db import models
from django.utils import timezone

logger = logging.getLogger(__name__)


class Room(models.Model):
    # core
    name        = models.CharField(max_length=80, unique=True)
    price       = models.DecimalField(max_digits=8, decimal_places=2)
    capacity    = models.PositiveIntegerField(default=2)
    description = models.TextField(blank=True)

    # extra details
    floor       = models.PositiveIntegerField(null=True, blank=True)
    size_sqm    = models.PositiveIntegerField(null=True, blank=True, help_text="Area in square meters")
    bed_count   = models.PositiveIntegerField(default=1)
    BED_TYPES   = [
        ('single','Single'),
        ('double','Double'),
        ('queen','Queen'),
        ('king','King'),
    ]
    bed_type    = models.CharField(max_length=10, choices=BED_TYPES, default='double')
    view_type   = models.CharField(
        max_length=20,
        choices=[('none','No View'),('sea','Sea View'),('garden','Garden View'),('city','City View')],
        default='none'
    )
    amenities   = models.JSONField(
        default=list,
        help_text="List of amenities, e.g. ['wifi','ac','minibar']"
    )

    # status & housekeeping
    is_active         = models.BooleanField(default=True)
    under_maintenance = models.BooleanField(default=False)

    # audit
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class RoomImage(models.Model):
    room    = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='images')
    image   = models.ImageField(upload_to='rooms/%Y/%m/%d/')
    caption = models.CharField(max_length=100, blank=True)
    order   = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.room.name} image #{self.order}"
    

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
    total_price      = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    status           = models.CharField(max_length=20, choices=STATUS_CHOICES, default='confirmed')
    created_at       = models.DateTimeField(default=timezone.now)
    additional_info  = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.guest_name} ({self.check_in}\u2192{self.check_out})"
    
    def get_total_price(self):
        total_price = sum(room.price for room in self.rooms.all())
        total_days  = (self.check_out - self.check_in).days
        return total_price * total_days
    
    class Meta:
        constraints = [
            models.CheckConstraint(check=models.Q(check_out__gt=models.F('check_in')), name='check_out_after_check_in'),
            models.CheckConstraint(check=models.Q(number_of_guests__gt=0), name='positive_guests'),
            models.CheckConstraint(check=models.Q(total_price__gte=0), name='positive_price')
        ]
        ordering = ['-created_at']


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


class Review(models.Model):
    reservation = models.ForeignKey(Reservation, on_delete=models.CASCADE, related_name='reviews')
    rating      = models.PositiveIntegerField()
    comment     = models.TextField(blank=True, null=True)
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.CheckConstraint(check=models.Q(rating__gte=1) & models.Q(rating__lte=5), name='valid_rating')
        ]
        ordering = ['-created_at']

    def __str__(self):
        return f"Review for {self.reservation.guest_name} ({self.rating}/5)"

logger.debug('Models loaded: %s, %s, %s', Room, Reservation, RoomClosure)


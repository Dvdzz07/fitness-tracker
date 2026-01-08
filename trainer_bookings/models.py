from django.db import models
from django.contrib.auth.models import User
from datetime import datetime


class TrainerBooking(models.Model):
    """
    Booking request for a training session with a trainer
    Priority based on earliest requested date/time
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('rejected', 'Rejected'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    client = models.ForeignKey(User, on_delete=models.CASCADE, related_name='client_bookings')
    trainer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='trainer_bookings')
    requested_date = models.DateField()
    requested_time = models.TimeField()
    duration_minutes = models.IntegerField(default=60)
    notes = models.TextField(blank=True, null=True)

    # Priority: timestamp of requested datetime (earlier = higher priority)
    priority_score = models.FloatField(default=0)

    # Status tracking
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ['priority_score', 'created_at']  # Lower score = earlier time = higher priority

    def __str__(self):
        return f"{self.client.username} -> {self.trainer.username} on {self.requested_date}"

    def calculate_priority(self):
        """
        Calculate priority score based on requested date/time
        Earlier = higher priority (lower score)
        """
        from .priority import calculate_booking_priority
        self.priority_score = calculate_booking_priority(self)
        self.save()


class TrainerAvailability(models.Model):
    """
    Defines when trainers are available for bookings
    """
    WEEKDAY_CHOICES = [
        (0, 'Monday'),
        (1, 'Tuesday'),
        (2, 'Wednesday'),
        (3, 'Thursday'),
        (4, 'Friday'),
        (5, 'Saturday'),
        (6, 'Sunday'),
    ]

    trainer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='availability_slots')
    weekday = models.IntegerField(choices=WEEKDAY_CHOICES)
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['weekday', 'start_time']

    def __str__(self):
        return f"{self.trainer.username} - {self.get_weekday_display()} {self.start_time}-{self.end_time}"


class BookingPriorityQueue(models.Model):
    """
    Queue entry for processing bookings in priority order
    Used by min-heap to maintain priority ordering
    """
    booking = models.ForeignKey(TrainerBooking, on_delete=models.CASCADE)
    heap_index = models.IntegerField(default=0)
    processed = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['heap_index']

    def __str__(self):
        return f"Queue entry for {self.booking} (index: {self.heap_index})"

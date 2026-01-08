from django.db import models
from django.contrib.auth.models import User


class Session(models.Model):
    """
    Fitness/sport session that users can create and join
    Sessions are displayed on a map using latitude/longitude
    """
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name="created_sessions")
    activity_name = models.CharField(max_length=100)
    date_time = models.DateTimeField()
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    capacity = models.IntegerField()
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date_time']

    def __str__(self):
        return f"{self.activity_name} - {self.date_time.strftime('%Y-%m-%d %H:%M')}"

    def get_current_participants_count(self):
        """Get number of users currently joined to this session"""
        return self.participants.count()

    def is_full(self):
        """Check if session has reached capacity"""
        return self.get_current_participants_count() >= self.capacity

    def has_user_joined(self, user):
        """Check if a specific user has already joined"""
        return self.participants.filter(user=user).exists()


class SessionParticipant(models.Model):
    """
    Link between users and sessions they have joined
    """
    session = models.ForeignKey(Session, on_delete=models.CASCADE, related_name="participants")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="joined_sessions")
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('session', 'user')
        ordering = ['joined_at']

    def __str__(self):
        return f"{self.user.username} joined {self.session.activity_name}"


class JoinRequestQueue(models.Model):
    """
    Queue for processing join requests in FIFO order
    Prevents race conditions when multiple users try to join simultaneously
    """
    session = models.ForeignKey(Session, on_delete=models.CASCADE, related_name="join_requests")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    processed = models.BooleanField(default=False)
    success = models.BooleanField(default=False)

    class Meta:
        ordering = ['timestamp']  # FIFO ordering

    def __str__(self):
        status = "Processed" if self.processed else "Pending"
        return f"{self.user.username} request for {self.session.activity_name} - {status}"

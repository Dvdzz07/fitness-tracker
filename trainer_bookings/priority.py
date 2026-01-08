# trainer_bookings/priority.py
# Simple priority calculation: earliest available trainer = highest priority

from datetime import datetime, date, timedelta


def calculate_booking_priority(booking):
    """
    Calculate priority based on requested date/time
    Earlier dates = higher priority (lower score)

    Args:
        booking: TrainerBooking object

    Returns:
        Priority score (timestamp as float, lower = earlier = higher priority)

    Algorithm:
    - Convert requested date/time to timestamp
    - Earlier timestamp = lower number = higher priority
    - Simple and efficient
    """
    # Combine date and time into datetime
    requested_datetime = datetime.combine(
        booking.requested_date,
        booking.requested_time
    )

    # Convert to timestamp (seconds since epoch)
    # Earlier times have lower timestamps = higher priority
    priority_score = requested_datetime.timestamp()

    return priority_score

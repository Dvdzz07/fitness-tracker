from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from datetime import datetime
from .models import TrainerBooking, TrainerAvailability


@login_required
def booking_list(request):
    """
    Display user's bookings
    Shows both client bookings and trainer bookings (if user is trainer)
    """
    # Get user's client bookings
    client_bookings = TrainerBooking.objects.filter(client=request.user).order_by('-created_at')

    # Get trainer bookings if user has trainer role
    trainer_bookings = []
    if hasattr(request.user, 'profile') and request.user.profile.role == 'trainer':
        trainer_bookings = TrainerBooking.objects.filter(trainer=request.user).order_by('priority_score')

    context = {
        'client_bookings': client_bookings,
        'trainer_bookings': trainer_bookings,
        'is_trainer': hasattr(request.user, 'profile') and request.user.profile.role == 'trainer'
    }
    return render(request, 'trainer_bookings/booking_list.html', context)


@login_required
def create_booking(request):
    """
    Create a new trainer booking request
    Calculates priority and adds to processing queue
    """
    # Get all trainers (users with trainer role)
    trainers = User.objects.filter(profile__role='trainer')

    if request.method == 'POST':
        trainer_id = request.POST.get('trainer')
        requested_date = request.POST.get('requested_date')
        requested_time = request.POST.get('requested_time')
        duration = request.POST.get('duration', 60)
        notes = request.POST.get('notes', '')

        trainer = get_object_or_404(User, id=trainer_id)

        # Create booking
        booking = TrainerBooking.objects.create(
            client=request.user,
            trainer=trainer,
            requested_date=requested_date,
            requested_time=requested_time,
            duration_minutes=duration,
            notes=notes
        )

        # Calculate priority (timestamp - earlier = higher priority)
        booking.calculate_priority()

        messages.success(request, f"Booking request submitted for {requested_date} at {requested_time}")
        return redirect('trainer_bookings:booking-list')

    context = {
        'trainers': trainers
    }
    return render(request, 'trainer_bookings/create_booking.html', context)


@login_required
def booking_detail(request, booking_id):
    """
    View details of a specific booking
    Shows priority breakdown
    """
    booking = get_object_or_404(TrainerBooking, id=booking_id)

    # Check user has permission to view
    if booking.client != request.user and booking.trainer != request.user:
        messages.error(request, "You don't have permission to view this booking")
        return redirect('trainer_bookings:booking-list')

    context = {
        'booking': booking,
        'is_trainer': booking.trainer == request.user
    }
    return render(request, 'trainer_bookings/booking_detail.html', context)


@login_required
def cancel_booking(request, booking_id):
    """
    Cancel a booking request
    """
    booking = get_object_or_404(TrainerBooking, id=booking_id, client=request.user)

    if booking.status == 'pending':
        booking.status = 'cancelled'
        booking.save()
        messages.success(request, "Booking cancelled")
    else:
        messages.warning(request, f"Cannot cancel booking with status: {booking.status}")

    return redirect('trainer_bookings:booking-list')


@login_required
def process_trainer_bookings(request, trainer_id):
    """
    Manually trigger processing of pending bookings for a trainer
    Uses priority queue (min-heap)
    """
    trainer = get_object_or_404(User, id=trainer_id)

    # Check user is the trainer
    if request.user != trainer:
        messages.error(request, "You can only process your own bookings")
        return redirect('trainer_bookings:booking-list')

    processed_count = process_booking_queue(trainer_id)

    messages.success(request, f"Processed {processed_count} booking requests using priority queue")
    return redirect('trainer_bookings:booking-list')


def process_booking_queue(trainer_id):
    """
    Process pending bookings in priority order (earliest first)

    Algorithm:
    1. Get all pending bookings for trainer
    2. Sort by priority_score (earlier times = lower score = higher priority)
    3. Confirm bookings that don't conflict
    4. Reject conflicting bookings

    Args:
        trainer_id: ID of trainer to process bookings for

    Returns:
        Number of bookings processed
    """
    # Get all pending bookings for this trainer, sorted by priority
    pending_bookings = TrainerBooking.objects.filter(
        trainer_id=trainer_id,
        status='pending'
    ).order_by('priority_score')  # Earlier times first

    if pending_bookings.count() == 0:
        return 0

    # Track confirmed booking times to detect conflicts
    confirmed_times = []
    processed_count = 0

    # Process bookings in priority order (earliest first)
    for booking in pending_bookings:
        # Check for time conflicts
        has_conflict = False
        for confirmed_time in confirmed_times:
            if (booking.requested_date == confirmed_time['date'] and
                booking.requested_time == confirmed_time['time']):
                has_conflict = True
                break

        if not has_conflict:
            # Confirm booking
            booking.status = 'confirmed'
            booking.processed_at = datetime.now()
            booking.save()

            # Track this time slot
            confirmed_times.append({
                'date': booking.requested_date,
                'time': booking.requested_time
            })

            processed_count += 1
        else:
            # Reject due to conflict
            booking.status = 'rejected'
            booking.processed_at = datetime.now()
            booking.save()
            processed_count += 1

    return processed_count


@login_required
def view_priority_queue(request, trainer_id):
    """
    View current priority queue for a trainer
    Shows bookings sorted by earliest date/time first
    """
    trainer = get_object_or_404(User, id=trainer_id)

    # Get pending bookings sorted by priority (earliest first)
    pending_bookings = TrainerBooking.objects.filter(
        trainer=trainer,
        status='pending'
    ).order_by('priority_score')

    # Build ordered list
    bookings_ordered = []
    for position, booking in enumerate(pending_bookings, start=1):
        bookings_ordered.append({
            'booking': booking,
            'position': position
        })

    context = {
        'trainer': trainer,
        'bookings_ordered': bookings_ordered,
        'total_pending': len(bookings_ordered)
    }
    return render(request, 'trainer_bookings/priority_queue.html', context)

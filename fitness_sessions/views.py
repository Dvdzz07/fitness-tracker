from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .models import Session, SessionParticipant, JoinRequestQueue
from .queue import SessionJoinQueue
from .stack import RecentSessionsStack


@login_required
def session_list(request):
    """
    Display all active sessions on a map using Leaflet.js
    Users can view sessions as pins on the map
    """
    sessions = Session.objects.all()

    # Get recently viewed sessions from Django session (stored as stack)
    recent_session_ids = request.session.get('recent_sessions', [])
    recent_sessions = []
    if recent_session_ids:
        for session_id in recent_session_ids:
            try:
                session = Session.objects.get(id=session_id)
                recent_sessions.append(session)
            except Session.DoesNotExist:
                pass

    context = {
        'sessions': sessions,
        'recent_sessions': recent_sessions
    }
    return render(request, 'fitness_sessions/session_list.html', context)


@login_required
def create_session(request):
    """
    Create a new fitness/sport session
    Users can specify activity, date/time, location, and capacity
    """
    if request.method == 'POST':
        activity_name = request.POST.get('activity_name')
        date_time = request.POST.get('date_time')
        latitude = request.POST.get('latitude')
        longitude = request.POST.get('longitude')
        capacity = request.POST.get('capacity')
        description = request.POST.get('description', '')

        # Create session
        session = Session.objects.create(
            creator=request.user,
            activity_name=activity_name,
            date_time=date_time,
            latitude=latitude,
            longitude=longitude,
            capacity=capacity,
            description=description
        )

        messages.success(request, f"Session '{activity_name}' created successfully!")
        return redirect('fitness_sessions:session-list')

    return render(request, 'fitness_sessions/create_session.html')


@login_required
def session_detail(request, session_id):
    """
    View details of a specific session
    Uses stack data structure to track recently viewed sessions
    """
    session = get_object_or_404(Session, id=session_id)

    # Update recently viewed sessions using stack
    recent_session_ids = request.session.get('recent_sessions', [])

    # Create stack and load existing items
    stack = RecentSessionsStack(max_size=5)
    for sid in recent_session_ids:
        stack.push(sid)

    # Push current session to stack
    stack.push(session_id)

    # Save back to Django session
    request.session['recent_sessions'] = stack.items
    request.session.modified = True

    # Check if user already joined
    has_joined = session.has_user_joined(request.user)

    # Check if user is creator
    is_creator = session.creator == request.user

    # Get participants
    participants = session.participants.all()

    context = {
        'session': session,
        'has_joined': has_joined,
        'is_creator': is_creator,
        'participants': participants,
        'participants_count': session.get_current_participants_count(),
        'is_full': session.is_full()
    }
    return render(request, 'fitness_sessions/session_detail.html', context)


@login_required
def join_session(request, session_id):
    """
    Request to join a session
    Adds request to queue for processing
    """
    session = get_object_or_404(Session, id=session_id)

    # Check if user already joined
    if session.has_user_joined(request.user):
        messages.warning(request, "You have already joined this session!")
        return redirect('fitness_sessions:session-detail', session_id=session.id)

    # Create join request and add to queue
    join_request = JoinRequestQueue.objects.create(
        session=session,
        user=request.user
    )

    # Process the queue immediately
    process_join_queue(session.id)

    # Check if request was successful
    join_request.refresh_from_db()
    if join_request.success:
        messages.success(request, f"Successfully joined '{session.activity_name}'!")
    else:
        messages.error(request, "Session is full. Could not join.")

    return redirect('fitness_sessions:session-detail', session_id=session.id)


def process_join_queue(session_id):
    """
    Process all pending join requests for a session using queue data structure
    Implements FIFO (First In First Out) ordering

    Args:
        session_id: ID of the session to process requests for
    """
    session = Session.objects.get(id=session_id)

    # Create queue instance
    queue = SessionJoinQueue()

    # Load all pending requests from database (ordered by timestamp for FIFO)
    pending_requests = JoinRequestQueue.objects.filter(
        session=session,
        processed=False
    ).order_by('timestamp')

    # Enqueue all pending requests
    for request in pending_requests:
        queue.enqueue(request)

    # Process queue until empty
    while not queue.is_empty():
        # Dequeue next request (FIFO - first in, first out)
        current_request = queue.dequeue()

        # Get current participant count
        current_count = session.get_current_participants_count()

        # Check if session has capacity
        if current_count < session.capacity:
            # Add participant
            SessionParticipant.objects.create(
                session=session,
                user=current_request.user
            )

            # Mark request as processed and successful
            current_request.processed = True
            current_request.success = True
            current_request.save()
        else:
            # Session is full - mark as processed but not successful
            current_request.processed = True
            current_request.success = False
            current_request.save()

            # Session is full, stop processing remaining requests
            # (They will remain in queue as unprocessed)
            break


@login_required
def leave_session(request, session_id):
    """
    Leave a session that the user has joined
    """
    session = get_object_or_404(Session, id=session_id)

    try:
        participant = SessionParticipant.objects.get(session=session, user=request.user)
        participant.delete()
        messages.success(request, f"You have left '{session.activity_name}'")
    except SessionParticipant.DoesNotExist:
        messages.warning(request, "You are not a participant of this session")

    return redirect('fitness_sessions:session-detail', session_id=session.id)


@login_required
def get_sessions_json(request):
    """
    Return all sessions as JSON for map display
    Used by Leaflet.js to display pins on the map
    """
    sessions = Session.objects.all()

    sessions_data = []
    for session in sessions:
        sessions_data.append({
            'id': session.id,
            'activity_name': session.activity_name,
            'date_time': session.date_time.strftime('%Y-%m-%d %H:%M'),
            'latitude': float(session.latitude),
            'longitude': float(session.longitude),
            'capacity': session.capacity,
            'participants_count': session.get_current_participants_count(),
            'is_full': session.is_full(),
            'creator': session.creator.username
        })

    return JsonResponse({'sessions': sessions_data})

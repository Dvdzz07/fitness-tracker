from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .models import Exercise, Workout, WorkoutExercise, Set, ExerciseRating
from .difficulty import calculate_experience_weight
from .recommendations import get_exercise_recommendations


@login_required
def workout_list(request):
    """
    Display list of user's workouts
    Similar to Hevy workout history
    """
    workouts = Workout.objects.filter(user=request.user)

    context = {
        "workouts": workouts
    }
    return render(request, "workouts/workout_list.html", context)


@login_required
def workout_detail(request, workout_id):
    """
    View detailed workout with all exercises and sets
    """
    workout = get_object_or_404(Workout, id=workout_id, user=request.user)

    context = {
        "workout": workout
    }
    return render(request, "workouts/workout_detail.html", context)


@login_required
def create_workout(request):
    """
    Create new workout session
    """
    if request.method == "POST":
        workout_name = request.POST.get("workout_name", "Workout")

        # Create new workout
        workout = Workout.objects.create(
            user=request.user,
            name=workout_name
        )

        messages.success(request, f"Workout '{workout_name}' created!")
        return redirect("workouts:add-exercise", workout_id=workout.id)

    return render(request, "workouts/create_workout.html")


@login_required
def add_exercise(request, workout_id):
    """
    Add exercises to workout
    Similar to Hevy's exercise selection
    """
    workout = get_object_or_404(Workout, id=workout_id, user=request.user)

    if request.method == "POST":
        exercise_id = request.POST.get("exercise_id")

        if exercise_id:
            # User selected an exercise
            exercise = get_object_or_404(Exercise, id=exercise_id)

            # Get current max order
            max_order = workout.workout_exercises.count()

            # Create workout exercise
            workout_exercise = WorkoutExercise.objects.create(
                workout=workout,
                exercise=exercise,
                order=max_order
            )

            messages.success(request, f"Added {exercise.name} to workout!")
            return redirect("workouts:log-sets", workout_id=workout.id)

    # Get search query from GET parameters
    search_query = request.GET.get("search", "")

    # Get all exercises
    exercises = Exercise.objects.all()

    # Filter by search query if provided
    if search_query:
        exercises = exercises.filter(name__icontains=search_query)

    exercises = exercises.order_by("primary_muscle", "name")

    # Group exercises by muscle
    exercises_by_muscle = {}
    for exercise in exercises:
        muscle = exercise.get_primary_muscle_display()
        if muscle not in exercises_by_muscle:
            exercises_by_muscle[muscle] = []
        exercises_by_muscle[muscle].append(exercise)

    context = {
        "workout": workout,
        "exercises_by_muscle": exercises_by_muscle,
        "search_query": search_query
    }
    return render(request, "workouts/add_exercise.html", context)


@login_required
def log_sets(request, workout_id):
    """
    Log sets for workout exercises
    Main workout logging interface (like Hevy)
    """
    workout = get_object_or_404(Workout, id=workout_id, user=request.user)

    if request.method == "POST":
        action = request.POST.get("action")

        if action == "add_set":
            workout_exercise_id = request.POST.get("workout_exercise_id")
            weight = request.POST.get("weight")
            reps = request.POST.get("reps")
            set_type = request.POST.get("set_type", "normal")

            workout_exercise = get_object_or_404(WorkoutExercise, id=workout_exercise_id)

            # Get next set number
            max_set = workout_exercise.sets.count()

            # Create set
            Set.objects.create(
                workout_exercise=workout_exercise,
                set_number=max_set + 1,
                weight=weight if weight else None,
                reps=reps if reps else None,
                set_type=set_type,
                completed=True
            )

            messages.success(request, "Set added!")
            return redirect("workouts:log-sets", workout_id=workout.id)

        elif action == "finish_workout":
            workout.completed = True
            workout.save()

            # Calculate workout difficulty score
            workout.calculate_and_save_difficulty()

            messages.success(request, "Workout completed!")
            return redirect("workouts:rate-exercises", workout_id=workout.id)

    context = {
        "workout": workout
    }
    return render(request, "workouts/log_sets.html", context)


@login_required
def delete_set(request, set_id):
    """
    Delete a set from workout
    """
    set_obj = get_object_or_404(Set, id=set_id)
    workout_id = set_obj.workout_exercise.workout.id

    # Check user owns this workout
    if set_obj.workout_exercise.workout.user == request.user:
        set_obj.delete()
        messages.success(request, "Set deleted!")

    return redirect("workouts:log-sets", workout_id=workout_id)


@login_required
def delete_workout_exercise(request, workout_exercise_id):
    """
    Remove exercise from workout
    """
    workout_exercise = get_object_or_404(WorkoutExercise, id=workout_exercise_id)
    workout_id = workout_exercise.workout.id

    # Check user owns this workout
    if workout_exercise.workout.user == request.user:
        exercise_name = workout_exercise.exercise.name
        workout_exercise.delete()
        messages.success(request, f"Removed {exercise_name} from workout!")

    return redirect("workouts:log-sets", workout_id=workout_id)


@login_required
def rate_exercises(request, workout_id):
    """
    Allow user to rate exercises after completing workout
    Uses logarithmic weighting based on user experience
    """
    workout = get_object_or_404(Workout, id=workout_id, user=request.user)

    if request.method == "POST":
        # Get user's total workout count (experience)
        user_workout_count = Workout.objects.filter(user=request.user, completed=True).count()

        # Calculate experience weight using logarithmic function
        experience_weight = calculate_experience_weight(user_workout_count)

        # Process each exercise rating
        for workout_exercise in workout.workout_exercises.all():
            rating_key = f"rating_{workout_exercise.id}"
            rating_value = request.POST.get(rating_key)

            if rating_value:
                # Convert to integer
                rating_value = int(rating_value)

                # Create rating record
                ExerciseRating.objects.create(
                    exercise=workout_exercise.exercise,
                    user=request.user,
                    rating=rating_value,
                    user_workout_count=user_workout_count,
                    experience_weight=experience_weight
                )

                # Update exercise difficulty (O(1) incremental update)
                workout_exercise.exercise.update_difficulty_from_rating(
                    rating_value,
                    experience_weight
                )

        messages.success(request, "Thank you for rating the exercises!")
        return redirect("workouts:workout-detail", workout_id=workout.id)

    context = {
        "workout": workout
    }
    return render(request, "workouts/rate_exercises.html", context)


@login_required
def recommend_exercises(request, workout_id):
    """
    Show recommended exercises using cosine similarity algorithm
    """
    workout = get_object_or_404(Workout, id=workout_id, user=request.user)

    if request.method == "POST":
        # Get user preferences from form
        user_preferences = {
            'strength': int(request.POST.get('strength', 5)),
            'cardio': int(request.POST.get('cardio', 5)),
            'flexibility': int(request.POST.get('flexibility', 5)),
            'upper_body': int(request.POST.get('upper_body', 5)),
            'lower_body': int(request.POST.get('lower_body', 5)),
            'core': int(request.POST.get('core', 5)),
            'preferred_difficulty': int(request.POST.get('preferred_difficulty', 5))
        }

        # Get recommendations using the algorithm
        recommended_exercises = get_exercise_recommendations(request.user, workout, user_preferences)

        context = {
            "workout": workout,
            "recommended_exercises": recommended_exercises
        }
        return render(request, "workouts/recommended_exercises.html", context)

    # GET request - show the preference form
    context = {
        "workout": workout,
        "recommended_exercises": None
    }
    return render(request, "workouts/recommended_exercises.html", context)

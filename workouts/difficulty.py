# workouts/difficulty.py
# Difficulty Scoring Algorithms for NEA
# Uses manual matrix multiplication and logarithmic weighting

import math


def calculate_experience_weight(workout_count):
    """
    Calculate experience weight using logarithmic scaling

    More experienced users (more workouts) have higher weight
    But growth slows down to prevent extreme dominance

    Args:
        workout_count: Total number of workouts user has completed

    Returns:
        weight: Experience weight value
    """
    # Add 1 to prevent log(0) and ensure minimum weight
    weight = 1 + math.log(workout_count + 1)
    return weight


def update_exercise_difficulty(exercise, new_rating, new_weight):
    """
    Update exercise difficulty score incrementally (O(1) efficiency)

    Instead of recalculating from all ratings, we update running totals
    This is much more efficient

    Args:
        exercise: Exercise object to update
        new_rating: New rating value (1-10)
        new_weight: Experience weight for this rating
    """
    # Step 1: Add new weighted rating to total
    weighted_rating = new_rating * new_weight
    # Convert Decimal to float for arithmetic
    current_weighted_sum = float(exercise.total_weighted_sum)
    exercise.total_weighted_sum = current_weighted_sum + weighted_rating

    # Step 2: Add new weight to total
    # Convert Decimal to float for arithmetic
    current_total_weight = float(exercise.total_weight)
    exercise.total_weight = current_total_weight + new_weight

    # Step 3: Recalculate difficulty score
    if exercise.total_weight > 0:
        exercise.difficulty_score = exercise.total_weighted_sum / exercise.total_weight
    else:
        exercise.difficulty_score = 5.0  # Default if no ratings

    # Save changes to database
    exercise.save()


def calculate_exercise_difficulty_manual(ratings_list, weights_list):
    """
    Calculate difficulty score using manual matrix multiplication
    This is for NEA demonstration - showing the algorithm step by step

    Args:
        ratings_list: List of rating values
        weights_list: List of corresponding weights

    Returns:
        difficulty_score: Weighted average of ratings
    """
    # Step 1: Calculate weighted sum using manual loop (matrix multiplication)
    weighted_sum = 0
    for i in range(len(ratings_list)):
        weighted_sum = weighted_sum + (ratings_list[i] * weights_list[i])

    # Step 2: Calculate total weight using manual loop
    total_weight = 0
    for weight in weights_list:
        total_weight = total_weight + weight

    # Step 3: Calculate final score (weighted average)
    if total_weight > 0:
        difficulty_score = weighted_sum / total_weight
    else:
        difficulty_score = 5.0  # Default

    return difficulty_score


def calculate_workout_difficulty(workout):
    """
    Calculate workout difficulty score out of 100

    Uses multiple factors:
    - Exercise difficulty ratings (40 points)
    - Total volume lifted (20 points)
    - Total reps completed (15 points)
    - Number of sets (10 points)
    - Progression from previous workout (15 points)

    Args:
        workout: Workout object

    Returns:
        difficulty_score: Score out of 100
    """
    # Step 1: Get all exercises in workout
    workout_exercises = workout.workout_exercises.all()

    if workout_exercises.count() == 0:
        return 0

    # Step 2: Exercise Difficulty Component (40 points max)
    # Average difficulty of exercises, scaled to 40 points
    total_exercise_difficulty = 0
    exercise_count = 0
    for workout_exercise in workout_exercises:
        exercise_score = float(workout_exercise.exercise.difficulty_score)
        total_exercise_difficulty = total_exercise_difficulty + exercise_score
        exercise_count = exercise_count + 1

    if exercise_count > 0:
        average_exercise_difficulty = total_exercise_difficulty / exercise_count
        # Scale from 0-10 to 0-40
        exercise_difficulty_points = (average_exercise_difficulty / 10) * 40
    else:
        exercise_difficulty_points = 0

    # Step 3: Volume Component (20 points max)
    # Total weight lifted, scaled logarithmically
    total_volume = 0
    for workout_exercise in workout_exercises:
        for set_obj in workout_exercise.sets.all():
            if set_obj.weight and set_obj.reps:
                volume = float(set_obj.weight) * set_obj.reps
                total_volume = total_volume + volume

    # Scale volume: 1000kg = 10 points, 5000kg = 20 points (logarithmic)
    if total_volume > 0:
        volume_points = min(20, (math.log(total_volume + 1) / math.log(5000)) * 20)
    else:
        volume_points = 0

    # Step 4: Reps Component (15 points max)
    # Total reps completed
    total_reps = 0
    for workout_exercise in workout_exercises:
        for set_obj in workout_exercise.sets.all():
            if set_obj.reps:
                total_reps = total_reps + set_obj.reps

    # Scale reps: 100 reps = 15 points max
    reps_points = min(15, (total_reps / 100) * 15)

    # Step 5: Sets Component (10 points max)
    # Total number of sets
    total_sets = 0
    for workout_exercise in workout_exercises:
        total_sets = total_sets + workout_exercise.sets.count()

    # Scale sets: 20 sets = 10 points max
    sets_points = min(10, (total_sets / 20) * 10)

    # Step 6: Progression Component (15 points max)
    # Compare to previous workout with same exercises
    progression_points = calculate_progression_bonus(workout)

    # Step 7: Sum all components to get final score out of 100
    difficulty_score = (exercise_difficulty_points + volume_points +
                       reps_points + sets_points + progression_points)

    # Ensure score stays within 0-100 range
    if difficulty_score > 100:
        difficulty_score = 100
    if difficulty_score < 0:
        difficulty_score = 0

    return difficulty_score


def calculate_progression_bonus(workout):
    """
    Calculate progression bonus by comparing to previous workouts

    Gives points for:
    - Lifting more weight than before
    - Doing more reps than before
    - Doing more sets than before

    Args:
        workout: Current workout object

    Returns:
        progression_points: Points out of 15
    """
    # Import here to avoid circular import
    from workouts.models import Workout

    # Get user's previous completed workouts
    previous_workouts = Workout.objects.filter(
        user=workout.user,
        completed=True
    ).exclude(id=workout.id).order_by('-date')

    if previous_workouts.count() == 0:
        # No previous workout to compare, give baseline 7.5 points
        return 7.5

    # Get most recent previous workout
    previous_workout = previous_workouts.first()

    # Calculate current workout metrics
    current_volume = 0
    current_reps = 0
    current_sets = 0

    for workout_exercise in workout.workout_exercises.all():
        for set_obj in workout_exercise.sets.all():
            if set_obj.weight and set_obj.reps:
                current_volume = current_volume + (float(set_obj.weight) * set_obj.reps)
            if set_obj.reps:
                current_reps = current_reps + set_obj.reps
        current_sets = current_sets + workout_exercise.sets.count()

    # Calculate previous workout metrics
    previous_volume = 0
    previous_reps = 0
    previous_sets = 0

    for workout_exercise in previous_workout.workout_exercises.all():
        for set_obj in workout_exercise.sets.all():
            if set_obj.weight and set_obj.reps:
                previous_volume = previous_volume + (float(set_obj.weight) * set_obj.reps)
            if set_obj.reps:
                previous_reps = previous_reps + set_obj.reps
        previous_sets = previous_sets + workout_exercise.sets.count()

    # Calculate percentage improvements
    progression_points = 0

    # Volume improvement (max 8 points)
    if previous_volume > 0:
        volume_improvement = ((current_volume - previous_volume) / previous_volume) * 100
        # 10% improvement = 4 points, 20% = 8 points, capped at 8
        volume_progression = min(8, max(0, (volume_improvement / 20) * 8))
        progression_points = progression_points + volume_progression
    else:
        progression_points = progression_points + 4  # Baseline

    # Reps improvement (max 4 points)
    if previous_reps > 0:
        reps_improvement = ((current_reps - previous_reps) / previous_reps) * 100
        reps_progression = min(4, max(0, (reps_improvement / 20) * 4))
        progression_points = progression_points + reps_progression
    else:
        progression_points = progression_points + 2  # Baseline

    # Sets improvement (max 3 points)
    if previous_sets > 0:
        sets_improvement = ((current_sets - previous_sets) / previous_sets) * 100
        sets_progression = min(3, max(0, (sets_improvement / 20) * 3))
        progression_points = progression_points + sets_progression
    else:
        progression_points = progression_points + 1.5  # Baseline

    return progression_points


def calculate_workout_difficulty_batch(workouts_list):
    """
    Calculate difficulty for multiple workouts using matrix operations
    Demonstrates batch processing

    Args:
        workouts_list: List of Workout objects

    Returns:
        difficulty_scores: List of difficulty scores
    """
    difficulty_scores = []

    # Calculate score for each workout
    for workout in workouts_list:
        score = calculate_workout_difficulty(workout)
        difficulty_scores.append(score)

    return difficulty_scores

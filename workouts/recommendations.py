# workouts/recommendations.py
# Exercise Recommendation Algorithm using Cosine Similarity and Recursive Filtering

import math


def calculate_cosine_similarity(vector_a, vector_b):
    """
    Calculate cosine similarity between two vectors using manual implementation

    Cosine similarity = (A · B) / (||A|| × ||B||)
    Where:
    - A · B is the dot product
    - ||A|| and ||B|| are the magnitudes (lengths) of the vectors

    Args:
        vector_a: First feature vector (list of numbers)
        vector_b: Second feature vector (list of numbers)

    Returns:
        similarity: Value between 0 and 1 (1 = perfect match)
    """
    # Step 1: Calculate dot product (A · B)
    dot_product = 0
    for i in range(len(vector_a)):
        dot_product = dot_product + (vector_a[i] * vector_b[i])

    # Step 2: Calculate magnitude of vector_a (||A||)
    magnitude_a = 0
    for value in vector_a:
        magnitude_a = magnitude_a + (value * value)
    magnitude_a = math.sqrt(magnitude_a)

    # Step 3: Calculate magnitude of vector_b (||B||)
    magnitude_b = 0
    for value in vector_b:
        magnitude_b = magnitude_b + (value * value)
    magnitude_b = math.sqrt(magnitude_b)

    # Step 4: Calculate cosine similarity
    if magnitude_a > 0 and magnitude_b > 0:
        similarity = dot_product / (magnitude_a * magnitude_b)
    else:
        similarity = 0

    return similarity


def get_exercise_vector(exercise):
    """
    Convert an exercise into a feature vector using stored database values

    Vector contains:
    [strength_focus, cardio_intensity, flexibility, upper_body, lower_body, core]

    Args:
        exercise: Exercise object

    Returns:
        vector: List of 6 numerical values
    """
    # Use pre-populated feature values from database
    vector = [
        exercise.strength_focus,
        exercise.cardio_intensity,
        exercise.flexibility,
        exercise.upper_body_involvement,
        exercise.lower_body_involvement,
        exercise.core_involvement
    ]

    return vector


def calculate_muscle_overuse_penalty(exercise, recent_muscle_usage, penalty_rate=0.2):
    """
    Calculate penalty for exercises targeting overused muscle groups

    Args:
        exercise: Exercise object
        recent_muscle_usage: Dictionary counting muscle group usage
        penalty_rate: Penalty per occurrence (default 0.2)

    Returns:
        penalty: Numerical penalty value
    """
    primary_muscle = exercise.primary_muscle

    # Count how many times this muscle appears in recent usage
    usage_count = recent_muscle_usage.get(primary_muscle, 0)

    # Calculate penalty
    penalty = usage_count * penalty_rate

    return penalty


def calculate_difficulty_penalty(exercise, preferred_difficulty, penalty_scale=0.1):
    """
    Calculate penalty based on difficulty mismatch

    Args:
        exercise: Exercise object
        preferred_difficulty: User's preferred difficulty (0-10)
        penalty_scale: How much to penalize per point of difference (default 0.1)

    Returns:
        penalty: Numerical penalty value
    """
    # Convert exercise difficulty to 0-10 scale (it's stored as DecimalField)
    exercise_difficulty = float(exercise.difficulty_score)

    # Calculate absolute difference
    difficulty_difference = abs(exercise_difficulty - preferred_difficulty)

    # Calculate penalty
    penalty = difficulty_difference * penalty_scale

    return penalty


def recommend_exercises_recursive(user_vector, candidate_exercises, recent_muscle_usage,
                                 recommendations, preferred_difficulty, max_recommendations=5):
    """
    Recursively select recommended exercises using cosine similarity

    Base Case: Stop when we have 5 recommendations or no candidates left

    Recursive Case:
    1. Calculate final score for each candidate
    2. Select exercise with highest score
    3. Remove from candidates and update muscle usage
    4. Recurse to select next exercise

    Args:
        user_vector: User's preference vector from form input
        candidate_exercises: List of Exercise objects to choose from
        recent_muscle_usage: Dictionary tracking muscle group usage
        recommendations: List to accumulate selected exercises
        preferred_difficulty: User's preferred difficulty level (0-10)
        max_recommendations: Maximum number to recommend (default 5)

    Returns:
        recommendations: List of recommended Exercise objects
    """
    # BASE CASE: Stop if we have enough recommendations or no candidates
    if len(recommendations) >= max_recommendations:
        return recommendations

    if len(candidate_exercises) == 0:
        return recommendations

    # Calculate scores for all candidates
    best_exercise = None
    best_score = -999  # Very low starting value

    for exercise in candidate_exercises:
        # Get exercise feature vector
        exercise_vector = get_exercise_vector(exercise)

        # Calculate cosine similarity (suitability score)
        similarity = calculate_cosine_similarity(user_vector, exercise_vector)

        # Calculate muscle overuse penalty
        muscle_penalty = calculate_muscle_overuse_penalty(exercise, recent_muscle_usage)

        # Calculate difficulty mismatch penalty
        difficulty_penalty = calculate_difficulty_penalty(exercise, preferred_difficulty)

        # Calculate final score
        final_score = similarity - muscle_penalty - difficulty_penalty

        # Track best exercise
        if final_score > best_score:
            best_score = final_score
            best_exercise = exercise

    # If we found a best exercise, add it to recommendations
    if best_exercise is not None:
        # Add to recommendations list
        recommendations.append(best_exercise)

        # Remove from candidates
        remaining_candidates = []
        for exercise in candidate_exercises:
            if exercise.id != best_exercise.id:
                remaining_candidates.append(exercise)

        # Update muscle usage tracking
        muscle = best_exercise.primary_muscle
        if muscle in recent_muscle_usage:
            recent_muscle_usage[muscle] = recent_muscle_usage[muscle] + 1
        else:
            recent_muscle_usage[muscle] = 1

        # RECURSIVE CALL: Select next exercise
        return recommend_exercises_recursive(
            user_vector,
            remaining_candidates,
            recent_muscle_usage,
            recommendations,
            preferred_difficulty,
            max_recommendations
        )

    # If no exercise found, return what we have
    return recommendations


def get_exercise_recommendations(user, workout, user_preferences):
    """
    Main function to get exercise recommendations for a user

    Args:
        user: User object
        workout: Current Workout object
        user_preferences: Dictionary with user's preference ratings (out of 10):
            {
                'strength': 7,
                'cardio': 5,
                'flexibility': 6,
                'upper_body': 8,
                'lower_body': 4,
                'core': 6,
                'preferred_difficulty': 5
            }

    Returns:
        recommendations: List of up to 5 recommended Exercise objects
    """
    from workouts.models import Exercise, Workout

    # Create user preference vector from form input
    user_vector = [
        user_preferences['strength'],
        user_preferences['cardio'],
        user_preferences['flexibility'],
        user_preferences['upper_body'],
        user_preferences['lower_body'],
        user_preferences['core']
    ]

    # Extract preferred difficulty
    preferred_difficulty = user_preferences.get('preferred_difficulty', 5)

    # Get all available exercises
    all_exercises = Exercise.objects.all()

    # Get exercises already in this workout
    current_exercise_ids = []
    for workout_exercise in workout.workout_exercises.all():
        current_exercise_ids.append(workout_exercise.exercise.id)

    # Filter to only candidates not already in workout
    candidate_exercises = []
    for exercise in all_exercises:
        if exercise.id not in current_exercise_ids:
            candidate_exercises.append(exercise)

    # Initialize muscle usage tracking from recent workouts
    recent_muscle_usage = {}

    recent_workouts = Workout.objects.filter(user=user, completed=True).order_by('-date')[:3]
    for past_workout in recent_workouts:
        for workout_exercise in past_workout.workout_exercises.all():
            muscle = workout_exercise.exercise.primary_muscle
            if muscle in recent_muscle_usage:
                recent_muscle_usage[muscle] = recent_muscle_usage[muscle] + 1
            else:
                recent_muscle_usage[muscle] = 1

    # Also track muscles in current workout
    for workout_exercise in workout.workout_exercises.all():
        muscle = workout_exercise.exercise.primary_muscle
        if muscle in recent_muscle_usage:
            recent_muscle_usage[muscle] = recent_muscle_usage[muscle] + 1
        else:
            recent_muscle_usage[muscle] = 1

    # Call recursive recommendation algorithm
    recommendations = []
    recommendations = recommend_exercises_recursive(
        user_vector,
        candidate_exercises,
        recent_muscle_usage,
        recommendations,
        preferred_difficulty,
        max_recommendations=5
    )

    return recommendations

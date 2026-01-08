from django.db import models
from django.contrib.auth.models import User


class Exercise(models.Model):
    """
    Exercise library - predefined exercises users can add to workouts
    Based on comprehensive bodybuilding exercise lists
    """

    MUSCLE_GROUP_CHOICES = [
        ("chest", "Chest"),
        ("back", "Back"),
        ("shoulders", "Shoulders"),
        ("biceps", "Biceps"),
        ("triceps", "Triceps"),
        ("legs", "Legs"),
        ("quads", "Quadriceps"),
        ("hamstrings", "Hamstrings"),
        ("glutes", "Glutes"),
        ("calves", "Calves"),
        ("abs", "Abdominals"),
        ("forearms", "Forearms"),
        ("full_body", "Full Body"),
        ("cardio", "Cardio"),
    ]

    EXERCISE_TYPE_CHOICES = [
        ("compound", "Compound"),
        ("isolation", "Isolation"),
        ("cardio", "Cardio"),
    ]

    name = models.CharField(max_length=100, unique=True)
    primary_muscle = models.CharField(max_length=20, choices=MUSCLE_GROUP_CHOICES)
    secondary_muscles = models.CharField(max_length=200, blank=True, null=True)
    exercise_type = models.CharField(max_length=20, choices=EXERCISE_TYPE_CHOICES)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    # Difficulty score fields for incremental O(1) updates
    total_weighted_sum = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_weight = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    difficulty_score = models.DecimalField(max_digits=5, decimal_places=2, default=5.0)

    # Exercise feature vector fields for cosine similarity (out of 10)
    strength_focus = models.IntegerField(default=5)
    cardio_intensity = models.IntegerField(default=0)
    flexibility = models.IntegerField(default=4)
    upper_body_involvement = models.IntegerField(default=0)
    lower_body_involvement = models.IntegerField(default=0)
    core_involvement = models.IntegerField(default=0)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.get_primary_muscle_display()})"

    def update_difficulty_from_rating(self, rating_value, user_weight):
        """
        Update difficulty score with new rating (O(1) incremental update)
        """
        from .difficulty import update_exercise_difficulty
        update_exercise_difficulty(self, rating_value, user_weight)


class Workout(models.Model):
    """
    Workout session logged by user
    Similar to Hevy workout logging
    """

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="workouts")
    name = models.CharField(max_length=100, default="Workout")
    date = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True, null=True)
    duration_minutes = models.IntegerField(blank=True, null=True)
    completed = models.BooleanField(default=False)
    difficulty_score = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    class Meta:
        ordering = ["-date"]

    def __str__(self):
        return f"{self.user.username} - {self.name} ({self.date.strftime('%Y-%m-%d')})"

    def get_total_sets(self):
        """Calculate total sets in workout"""
        total = 0
        for workout_exercise in self.workout_exercises.all():
            total += workout_exercise.sets.count()
        return total

    def get_total_volume(self):
        """Calculate total volume (weight x reps) for workout"""
        total_volume = 0
        for workout_exercise in self.workout_exercises.all():
            for set_obj in workout_exercise.sets.all():
                if set_obj.weight and set_obj.reps:
                    total_volume += set_obj.weight * set_obj.reps
        return total_volume

    def calculate_and_save_difficulty(self):
        """
        Calculate workout difficulty using matrix multiplication
        and save to database
        """
        from .difficulty import calculate_workout_difficulty
        score = calculate_workout_difficulty(self)
        self.difficulty_score = score
        self.save()


class WorkoutExercise(models.Model):
    """
    Links exercises to workouts
    Acts as intermediary between Workout and Exercise
    """

    workout = models.ForeignKey(Workout, on_delete=models.CASCADE, related_name="workout_exercises")
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE)
    order = models.IntegerField(default=0)
    notes = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return f"{self.workout.name} - {self.exercise.name}"


class Set(models.Model):
    """
    Individual set within an exercise
    Tracks weight, reps, and set type (similar to Hevy)
    """

    SET_TYPE_CHOICES = [
        ("normal", "Normal"),
        ("warmup", "Warm-up"),
        ("failure", "To Failure"),
        ("drop", "Drop Set"),
    ]

    workout_exercise = models.ForeignKey(WorkoutExercise, on_delete=models.CASCADE, related_name="sets")
    set_number = models.IntegerField()
    weight = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    reps = models.IntegerField(blank=True, null=True)
    set_type = models.CharField(max_length=20, choices=SET_TYPE_CHOICES, default="normal")
    completed = models.BooleanField(default=False)
    notes = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ["set_number"]

    def __str__(self):
        return f"Set {self.set_number}: {self.weight}kg x {self.reps} reps ({self.get_set_type_display()})"


class ExerciseRating(models.Model):
    """
    User rating for an exercise
    Stores individual ratings with user experience at time of rating
    """

    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE, related_name="ratings")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField()  # 1-10 scale
    user_workout_count = models.IntegerField()  # User's total workouts when rating was given
    experience_weight = models.DecimalField(max_digits=10, decimal_places=4)  # Calculated weight
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.username} rated {self.exercise.name}: {self.rating}/10"

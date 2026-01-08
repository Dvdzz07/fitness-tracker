from django.contrib import admin
from .models import Exercise, Workout, WorkoutExercise, Set, ExerciseRating

admin.site.register(Exercise)
admin.site.register(Workout)
admin.site.register(WorkoutExercise)
admin.site.register(Set)
admin.site.register(ExerciseRating)

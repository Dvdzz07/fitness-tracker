from django.core.management.base import BaseCommand
from workouts.models import Exercise


class Command(BaseCommand):
    help = 'Populates the exercise database with common exercises'

    def handle(self, *args, **kwargs):
        exercises = [
            # CHEST EXERCISES
            {"name": "Barbell Bench Press", "primary_muscle": "chest", "secondary_muscles": "triceps,shoulders", "exercise_type": "compound"},
            {"name": "Incline Barbell Bench Press", "primary_muscle": "chest", "secondary_muscles": "triceps,shoulders", "exercise_type": "compound"},
            {"name": "Decline Barbell Bench Press", "primary_muscle": "chest", "secondary_muscles": "triceps,shoulders", "exercise_type": "compound"},
            {"name": "Dumbbell Bench Press", "primary_muscle": "chest", "secondary_muscles": "triceps,shoulders", "exercise_type": "compound"},
            {"name": "Incline Dumbbell Press", "primary_muscle": "chest", "secondary_muscles": "triceps,shoulders", "exercise_type": "compound"},
            {"name": "Dumbbell Fly", "primary_muscle": "chest", "secondary_muscles": "", "exercise_type": "isolation"},
            {"name": "Cable Fly", "primary_muscle": "chest", "secondary_muscles": "", "exercise_type": "isolation"},
            {"name": "Push-up", "primary_muscle": "chest", "secondary_muscles": "triceps,shoulders", "exercise_type": "compound"},
            {"name": "Chest Dip", "primary_muscle": "chest", "secondary_muscles": "triceps,shoulders", "exercise_type": "compound"},
            {"name": "Pec Deck Machine", "primary_muscle": "chest", "secondary_muscles": "", "exercise_type": "isolation"},

            # BACK EXERCISES
            {"name": "Deadlift", "primary_muscle": "back", "secondary_muscles": "legs,glutes,hamstrings", "exercise_type": "compound"},
            {"name": "Barbell Row", "primary_muscle": "back", "secondary_muscles": "biceps", "exercise_type": "compound"},
            {"name": "Dumbbell Row", "primary_muscle": "back", "secondary_muscles": "biceps", "exercise_type": "compound"},
            {"name": "T-Bar Row", "primary_muscle": "back", "secondary_muscles": "biceps", "exercise_type": "compound"},
            {"name": "Pull-up", "primary_muscle": "back", "secondary_muscles": "biceps", "exercise_type": "compound"},
            {"name": "Chin-up", "primary_muscle": "back", "secondary_muscles": "biceps", "exercise_type": "compound"},
            {"name": "Lat Pulldown", "primary_muscle": "back", "secondary_muscles": "biceps", "exercise_type": "compound"},
            {"name": "Seated Cable Row", "primary_muscle": "back", "secondary_muscles": "biceps", "exercise_type": "compound"},
            {"name": "Face Pull", "primary_muscle": "back", "secondary_muscles": "shoulders", "exercise_type": "isolation"},
            {"name": "Hyperextension", "primary_muscle": "back", "secondary_muscles": "glutes,hamstrings", "exercise_type": "isolation"},

            # SHOULDER EXERCISES
            {"name": "Overhead Press", "primary_muscle": "shoulders", "secondary_muscles": "triceps", "exercise_type": "compound"},
            {"name": "Dumbbell Shoulder Press", "primary_muscle": "shoulders", "secondary_muscles": "triceps", "exercise_type": "compound"},
            {"name": "Arnold Press", "primary_muscle": "shoulders", "secondary_muscles": "triceps", "exercise_type": "compound"},
            {"name": "Lateral Raise", "primary_muscle": "shoulders", "secondary_muscles": "", "exercise_type": "isolation"},
            {"name": "Front Raise", "primary_muscle": "shoulders", "secondary_muscles": "", "exercise_type": "isolation"},
            {"name": "Rear Delt Fly", "primary_muscle": "shoulders", "secondary_muscles": "", "exercise_type": "isolation"},
            {"name": "Upright Row", "primary_muscle": "shoulders", "secondary_muscles": "", "exercise_type": "compound"},
            {"name": "Shrugs", "primary_muscle": "shoulders", "secondary_muscles": "back", "exercise_type": "isolation"},

            # BICEPS EXERCISES
            {"name": "Barbell Curl", "primary_muscle": "biceps", "secondary_muscles": "", "exercise_type": "isolation"},
            {"name": "Dumbbell Curl", "primary_muscle": "biceps", "secondary_muscles": "", "exercise_type": "isolation"},
            {"name": "Hammer Curl", "primary_muscle": "biceps", "secondary_muscles": "forearms", "exercise_type": "isolation"},
            {"name": "Preacher Curl", "primary_muscle": "biceps", "secondary_muscles": "", "exercise_type": "isolation"},
            {"name": "Cable Curl", "primary_muscle": "biceps", "secondary_muscles": "", "exercise_type": "isolation"},
            {"name": "Concentration Curl", "primary_muscle": "biceps", "secondary_muscles": "", "exercise_type": "isolation"},

            # TRICEPS EXERCISES
            {"name": "Close-Grip Bench Press", "primary_muscle": "triceps", "secondary_muscles": "chest", "exercise_type": "compound"},
            {"name": "Tricep Dip", "primary_muscle": "triceps", "secondary_muscles": "chest,shoulders", "exercise_type": "compound"},
            {"name": "Overhead Tricep Extension", "primary_muscle": "triceps", "secondary_muscles": "", "exercise_type": "isolation"},
            {"name": "Tricep Pushdown", "primary_muscle": "triceps", "secondary_muscles": "", "exercise_type": "isolation"},
            {"name": "Skull Crusher", "primary_muscle": "triceps", "secondary_muscles": "", "exercise_type": "isolation"},
            {"name": "Diamond Push-up", "primary_muscle": "triceps", "secondary_muscles": "chest", "exercise_type": "compound"},

            # LEG EXERCISES
            {"name": "Barbell Squat", "primary_muscle": "quads", "secondary_muscles": "glutes,hamstrings", "exercise_type": "compound"},
            {"name": "Front Squat", "primary_muscle": "quads", "secondary_muscles": "glutes,hamstrings", "exercise_type": "compound"},
            {"name": "Leg Press", "primary_muscle": "quads", "secondary_muscles": "glutes,hamstrings", "exercise_type": "compound"},
            {"name": "Romanian Deadlift", "primary_muscle": "hamstrings", "secondary_muscles": "glutes,back", "exercise_type": "compound"},
            {"name": "Leg Curl", "primary_muscle": "hamstrings", "secondary_muscles": "", "exercise_type": "isolation"},
            {"name": "Leg Extension", "primary_muscle": "quads", "secondary_muscles": "", "exercise_type": "isolation"},
            {"name": "Lunges", "primary_muscle": "quads", "secondary_muscles": "glutes,hamstrings", "exercise_type": "compound"},
            {"name": "Bulgarian Split Squat", "primary_muscle": "quads", "secondary_muscles": "glutes,hamstrings", "exercise_type": "compound"},
            {"name": "Hip Thrust", "primary_muscle": "glutes", "secondary_muscles": "hamstrings", "exercise_type": "compound"},
            {"name": "Calf Raise", "primary_muscle": "calves", "secondary_muscles": "", "exercise_type": "isolation"},
            {"name": "Seated Calf Raise", "primary_muscle": "calves", "secondary_muscles": "", "exercise_type": "isolation"},

            # ABS/CORE EXERCISES
            {"name": "Plank", "primary_muscle": "abs", "secondary_muscles": "", "exercise_type": "isolation"},
            {"name": "Crunches", "primary_muscle": "abs", "secondary_muscles": "", "exercise_type": "isolation"},
            {"name": "Hanging Leg Raise", "primary_muscle": "abs", "secondary_muscles": "", "exercise_type": "isolation"},
            {"name": "Russian Twist", "primary_muscle": "abs", "secondary_muscles": "", "exercise_type": "isolation"},
            {"name": "Cable Crunch", "primary_muscle": "abs", "secondary_muscles": "", "exercise_type": "isolation"},
            {"name": "Ab Wheel Rollout", "primary_muscle": "abs", "secondary_muscles": "", "exercise_type": "isolation"},

            # CARDIO EXERCISES
            {"name": "Running", "primary_muscle": "cardio", "secondary_muscles": "legs", "exercise_type": "cardio"},
            {"name": "Walking", "primary_muscle": "cardio", "secondary_muscles": "legs", "exercise_type": "cardio"},
            {"name": "Rowing Machine", "primary_muscle": "cardio", "secondary_muscles": "back,legs", "exercise_type": "cardio"},
        ]

        created_count = 0
        for exercise_data in exercises:
            exercise, created = Exercise.objects.get_or_create(
                name=exercise_data["name"],
                defaults={
                    "primary_muscle": exercise_data["primary_muscle"],
                    "secondary_muscles": exercise_data["secondary_muscles"],
                    "exercise_type": exercise_data["exercise_type"],
                }
            )
            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f'Created exercise: {exercise.name}'))
            else:
                self.stdout.write(f'Exercise already exists: {exercise.name}')

        self.stdout.write(self.style.SUCCESS(f'\nTotal exercises created: {created_count}'))
        self.stdout.write(self.style.SUCCESS(f'Total exercises in database: {Exercise.objects.count()}'))

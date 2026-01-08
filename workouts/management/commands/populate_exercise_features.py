# workouts/management/commands/populate_exercise_features.py
# Populate exercise feature vectors based on online fitness research

from django.core.management.base import BaseCommand
from workouts.models import Exercise


class Command(BaseCommand):
    help = "Populate exercise feature vectors for recommendation algorithm"

    def handle(self, *args, **kwargs):
        # Exercise features: [strength, cardio, flexibility, upper, lower, core]
        # All values out of 10
        # Based on online fitness research and exercise biomechanics

        exercise_features = {
            # CHEST EXERCISES
            "Barbell Bench Press": [9, 0, 6, 10, 1, 3],
            "Incline Barbell Bench Press": [9, 0, 6, 10, 0, 3],
            "Decline Barbell Bench Press": [8, 0, 5, 10, 0, 2],
            "Dumbbell Bench Press": [8, 0, 7, 10, 1, 3],
            "Incline Dumbbell Press": [8, 0, 7, 10, 0, 3],
            "Dumbbell Fly": [6, 0, 8, 9, 0, 2],
            "Cable Fly": [5, 0, 7, 9, 0, 2],
            "Push-up": [6, 1, 6, 8, 0, 5],
            "Chest Dip": [8, 0, 6, 9, 0, 4],
            "Pec Deck Machine": [5, 0, 6, 9, 0, 1],

            # BACK EXERCISES
            "Deadlift": [10, 1, 7, 6, 10, 8],
            "Barbell Row": [9, 0, 6, 9, 5, 6],
            "Dumbbell Row": [8, 0, 7, 9, 3, 5],
            "T-Bar Row": [9, 0, 6, 9, 4, 6],
            "Pull-up": [9, 0, 7, 10, 0, 6],
            "Chin-up": [8, 0, 7, 10, 0, 6],
            "Lat Pulldown": [7, 0, 6, 9, 0, 4],
            "Seated Cable Row": [7, 0, 6, 9, 0, 5],
            "Face Pull": [5, 0, 7, 7, 0, 4],
            "Hyperextension": [6, 0, 8, 3, 7, 7],

            # SHOULDER EXERCISES
            "Overhead Press": [9, 0, 6, 10, 1, 7],
            "Dumbbell Shoulder Press": [8, 0, 7, 10, 0, 6],
            "Arnold Press": [8, 0, 8, 10, 0, 5],
            "Lateral Raise": [4, 0, 6, 8, 0, 2],
            "Front Raise": [4, 0, 6, 8, 0, 3],
            "Rear Delt Fly": [5, 0, 7, 7, 0, 3],
            "Upright Row": [6, 0, 6, 8, 0, 4],
            "Shrugs": [5, 0, 4, 6, 0, 2],

            # BICEPS EXERCISES
            "Barbell Curl": [6, 0, 5, 8, 0, 2],
            "Dumbbell Curl": [5, 0, 6, 8, 0, 2],
            "Hammer Curl": [5, 0, 6, 8, 0, 2],
            "Preacher Curl": [6, 0, 5, 9, 0, 1],
            "Cable Curl": [5, 0, 6, 8, 0, 2],
            "Concentration Curl": [5, 0, 6, 8, 0, 1],

            # TRICEPS EXERCISES
            "Close-Grip Bench Press": [8, 0, 6, 10, 0, 3],
            "Tricep Dip": [8, 0, 7, 9, 0, 4],
            "Overhead Tricep Extension": [6, 0, 7, 8, 0, 3],
            "Tricep Pushdown": [5, 0, 5, 8, 0, 2],
            "Skull Crusher": [7, 0, 6, 9, 0, 2],
            "Diamond Push-up": [6, 1, 6, 8, 0, 4],

            # LEG EXERCISES
            "Barbell Squat": [10, 1, 7, 1, 10, 8],
            "Front Squat": [9, 1, 8, 2, 10, 9],
            "Leg Press": [8, 0, 5, 0, 10, 4],
            "Romanian Deadlift": [9, 0, 8, 3, 9, 7],
            "Leg Curl": [5, 0, 6, 0, 8, 2],
            "Leg Extension": [5, 0, 5, 0, 9, 1],
            "Lunges": [7, 2, 8, 0, 9, 6],
            "Bulgarian Split Squat": [8, 1, 9, 0, 10, 7],
            "Hip Thrust": [7, 0, 7, 0, 8, 5],
            "Calf Raise": [4, 0, 5, 0, 7, 1],
            "Seated Calf Raise": [4, 0, 5, 0, 7, 0],

            # CORE/ABS EXERCISES
            "Plank": [3, 0, 5, 4, 0, 10],
            "Crunches": [2, 0, 4, 2, 0, 9],
            "Hanging Leg Raise": [5, 0, 7, 6, 0, 10],
            "Russian Twist": [3, 0, 6, 3, 0, 9],
            "Cable Crunch": [4, 0, 5, 3, 0, 9],
            "Ab Wheel Rollout": [6, 0, 8, 5, 0, 10],

            # CARDIO EXERCISES
            "Running": [2, 10, 6, 2, 8, 4],
            "Walking": [1, 6, 5, 1, 6, 2],
            "Rowing Machine": [4, 9, 7, 7, 8, 6],
        }

        updated_count = 0

        for exercise_name, features in exercise_features.items():
            try:
                exercise = Exercise.objects.get(name=exercise_name)

                # Unpack features
                strength, cardio, flexibility, upper, lower, core = features

                # Update exercise
                exercise.strength_focus = strength
                exercise.cardio_intensity = cardio
                exercise.flexibility = flexibility
                exercise.upper_body_involvement = upper
                exercise.lower_body_involvement = lower
                exercise.core_involvement = core

                exercise.save()
                updated_count = updated_count + 1

                self.stdout.write(
                    self.style.SUCCESS(f"Updated {exercise_name}: S:{strength} C:{cardio} F:{flexibility} U:{upper} L:{lower} Core:{core}")
                )

            except Exercise.DoesNotExist:
                self.stdout.write(
                    self.style.WARNING(f"Exercise '{exercise_name}' not found in database")
                )

        self.stdout.write(
            self.style.SUCCESS(f"\nSuccessfully updated {updated_count} exercises with feature vectors!")
        )

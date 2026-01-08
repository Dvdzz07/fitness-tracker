# workouts/management/commands/set_initial_ratings.py
# Set initial difficulty ratings for all exercises based on online research

from django.core.management.base import BaseCommand
from workouts.models import Exercise


class Command(BaseCommand):
    help = "Set initial difficulty ratings for all exercises based on fitness research"

    def handle(self, *args, **kwargs):
        # Initial difficulty ratings based on online fitness resources
        # Scale: 1-10 where 1=very easy, 10=very hard
        # Based on technical difficulty, strength requirements, and coordination needed

        exercise_ratings = {
            # Chest exercises
            "Barbell Bench Press": 7.5,
            "Incline Barbell Bench Press": 7.0,
            "Decline Barbell Bench Press": 6.5,
            "Dumbbell Bench Press": 7.0,
            "Incline Dumbbell Press": 6.5,
            "Dumbbell Fly": 5.0,
            "Cable Fly": 5.5,
            "Push-up": 4.0,
            "Chest Dip": 7.0,
            "Pec Deck Machine": 4.5,

            # Back exercises
            "Deadlift": 9.0,
            "Barbell Row": 7.5,
            "Dumbbell Row": 6.5,
            "T-Bar Row": 7.0,
            "Pull-up": 8.0,
            "Chin-up": 7.5,
            "Lat Pulldown": 5.5,
            "Seated Cable Row": 5.0,
            "Face Pull": 4.0,
            "Hyperextension": 5.5,

            # Shoulder exercises
            "Overhead Press": 7.5,
            "Dumbbell Shoulder Press": 7.0,
            "Arnold Press": 6.5,
            "Lateral Raise": 4.5,
            "Front Raise": 4.0,
            "Rear Delt Fly": 5.0,
            "Upright Row": 5.5,
            "Shrugs": 4.0,

            # Biceps exercises
            "Barbell Curl": 5.0,
            "Dumbbell Curl": 4.5,
            "Hammer Curl": 4.5,
            "Preacher Curl": 5.5,
            "Cable Curl": 4.0,
            "Concentration Curl": 4.0,

            # Triceps exercises
            "Close-Grip Bench Press": 7.0,
            "Tricep Dip": 6.5,
            "Overhead Tricep Extension": 5.5,
            "Tricep Pushdown": 4.0,
            "Skull Crusher": 6.0,
            "Diamond Push-up": 5.5,

            # Leg exercises
            "Barbell Squat": 8.5,
            "Front Squat": 8.0,
            "Leg Press": 6.0,
            "Romanian Deadlift": 7.5,
            "Leg Curl": 4.0,
            "Leg Extension": 3.5,
            "Lunges": 6.5,
            "Bulgarian Split Squat": 9.5,
            "Hip Thrust": 6.0,
            "Calf Raise": 3.0,
            "Seated Calf Raise": 3.0,

            # Core exercises
            "Plank": 5.0,
            "Crunches": 3.0,
            "Hanging Leg Raise": 7.0,
            "Russian Twist": 5.0,
            "Cable Crunch": 4.5,
            "Ab Wheel Rollout": 7.5,

            # Cardio exercises
            "Running": 6.0,
            "Walking": 2.0,
            "Rowing Machine": 6.5,
        }

        updated_count = 0

        for exercise_name, rating in exercise_ratings.items():
            try:
                exercise = Exercise.objects.get(name=exercise_name)

                # Set initial difficulty score
                exercise.difficulty_score = rating

                # Set initial weighted sum and weight based on rating
                # Use a base weight of 1.0 (representing one "average" user rating)
                initial_weight = 1.0
                exercise.total_weighted_sum = rating * initial_weight
                exercise.total_weight = initial_weight

                exercise.save()
                updated_count = updated_count + 1

                self.stdout.write(
                    self.style.SUCCESS(f"Set {exercise_name} to difficulty {rating}/10")
                )

            except Exercise.DoesNotExist:
                self.stdout.write(
                    self.style.WARNING(f"Exercise '{exercise_name}' not found in database")
                )

        self.stdout.write(
            self.style.SUCCESS(f"\nSuccessfully updated {updated_count} exercises with initial ratings!")
        )

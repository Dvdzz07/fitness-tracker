from django.urls import path
from . import views

app_name = "workouts"

urlpatterns = [
    path("", views.workout_list, name="workout-list"),
    path("create/", views.create_workout, name="create-workout"),
    path("<int:workout_id>/", views.workout_detail, name="workout-detail"),
    path("<int:workout_id>/add-exercise/", views.add_exercise, name="add-exercise"),
    path("<int:workout_id>/recommend/", views.recommend_exercises, name="recommend-exercises"),
    path("<int:workout_id>/log-sets/", views.log_sets, name="log-sets"),
    path("<int:workout_id>/rate/", views.rate_exercises, name="rate-exercises"),
    path("set/<int:set_id>/delete/", views.delete_set, name="delete-set"),
    path("workout-exercise/<int:workout_exercise_id>/delete/", views.delete_workout_exercise, name="delete-workout-exercise"),
]

from django.urls import path
from . import views

app_name = "program_builder"

urlpatterns = [
    path(
        'get-all-movements/',
        views.ajax_all_movements,
        name="ajax_all_movements",
    ),
    path('exercices/', views.exercises_list, name="exercises_list"),
    path('add-exercise/', views.add_exercise, name="add_exercise"),
    path('exercise/<exercise_pk>/', views.exercise_page, name="exercise_page"),
    path(
        'delete-exercise/<exercise_pk>/',
        views.delete_exercise,
        name="delete_exercise",
    ),
    path('trainings/', views.trainings_list, name="trainings_list"),
    path('profile/', views.profile, name="profile"),
]
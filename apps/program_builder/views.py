import json
from datetime import time, datetime
from django.shortcuts import render, redirect
from django.urls import reverse
from django.http import JsonResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.models import User
from .forms import RegisterExerciseStep1, PasswordChangeCustomForm
from .utils.db_interactions import DBMovement, DBExercise, DBTraining
from .utils.treatments import DataTreatment
from .utils.tools import Tools


def index(request):
    if request.user.is_authenticated:
        return redirect(reverse("program_builder:trainings_list"), locals())
    else:
        return redirect(reverse("users:log_in"), locals())


@login_required
def ajax_all_movements(request):
    """
    This view returns all the movements in JSON
    For JSON structure -> see JSONTreatments class > def get_all_movements
    in utils.treatments.py
    """
    treatment = DataTreatment()
    movements = treatment.get_all_movements_in_dict()

    return JsonResponse(movements, safe=False)


@csrf_protect
@login_required
def exercises_list(request):
    """
    This view manages the exercises:
        - print a list of exercise
        - create an exercise and redirect on the exercise page to finalize
    """
    tools = Tools()
    db = DataTreatment()
    exercises = db.get_all_exercises_dict_linked_to_one_user(request.user)
    for exercise in exercises:
        if exercise["pb"] != 0 and exercise["goal_type"] != "duree":
            exercise["pb"] = tools.convert_seconds_into_time(exercise["pb"])
    new_exercise_form = RegisterExerciseStep1()
    context = {
        'exercises': exercises,
        'exercises_number': len(exercises),
        'custom_exercises_number': len(
            [exercise for exercise in exercises if not exercise["is_default"]]
        ),
        'pb_number': len(
            [exercise for exercise in exercises if exercise["pb"] != 0]
        ),
        'new_exercise_form': new_exercise_form,
        'title': 'exercises',
    }
    return render(request, 'exercises_list.html', context)


@csrf_protect
@login_required
def add_exercise(request):
    if request.body:
        treatment = DataTreatment()
        exercise_dict = json.loads(request.body)

        new_exercise = treatment.register_exercise_from_dict(
            exercise_dict, request.user
        )
        return JsonResponse(new_exercise.pk, safe=False)
    else:
        messages.error(request, """Un problème a été rencontré.""")
        referer = request.META.get("HTTP_REFERER")
        return redirect(referer, locals())


@csrf_protect
@login_required
def exercise_page(request, exercise_pk):

    treatment = DataTreatment()
    exercise_dict = treatment.get_one_exercise_in_dict_linked_to_one_user(
        exercise_pk, request.user
    )
    context = {
        'exercise_dict': exercise_dict,
        'title': 'exercises',
        'date': datetime.now(),
    }
    if request.method == "POST":
        db_training = DBTraining()
        db_exercise = DBExercise()
        exercise = db_exercise.get_one_exercise_by_pk(exercise_dict["id"])
        training = db_training.set_training(exercise, request.user)
        if training:
            messages.success(
                request,
                """Votre entraînement a été créé. Donnez le maximum de vous même!""",
            )
            return redirect(reverse('program_builder:trainings_list'))
        else:
            messages.error(
                request,
                """Un problème a été rencontré lors de la création de votre entraînement. 
                                    Veuillez réessayer s'il vous plait.""",
            )
            return render(request, "exercise_page.html", context)
    else:
        return render(request, 'exercise_page.html', context)


@login_required
def delete_exercise(request, exercise_pk):
    """
    This view manages only the exercise's removal
    """
    db = DBExercise()
    deleted_exercise = db.del_exercise(exercise_pk)
    messages.success(request, """L'exercice a été supprimé.""")

    referer = request.META.get("HTTP_REFERER")
    return redirect(referer, locals())


@login_required
def trainings_list(request):

    tools = Tools()
    if request.method == "POST":
        db_training = DBTraining()
        training_pk = request.POST.get("training_pk")
        performance_value = request.POST.get("performance_value")
        training = db_training.get_one_training_from_pk(training_pk)

        if training:
            # For trainings with time as performance_type, we convert string from input type=time in seconds(int)
            if training.performance_type == "duree":
                performance_value = tools.convert_string_time_into_int_seconds(
                    performance_value
                )

            # We register the new performance_value
            training.performance_value = performance_value
            training.done = True
            training.save()

    db = DataTreatment()
    trainings = db.get_all_trainings_per_user_in_dict(request.user)

    # For trainings with time as performance_type, we convert performance_value and pb in time
    for training in trainings:
        if (
            training["performance_value"]
            and training["performance_type"] == "duree"
        ):
            training["performance_value"] = tools.convert_seconds_into_time(
                training["performance_value"]
            )
            training["exercise"]["pb"] = tools.convert_seconds_into_time(
                training["exercise"]["pb"]
            )

    context = {
        "title": 'trainings',
        "trainings": trainings,
        "trainings_number": len(trainings),
        "trainings_done_number": len(
            [training for training in trainings if training["done"]]
        ),
        "pb_number": len(
            [
                training
                for training in trainings
                if training["performance_value"]
                and training["performance_value"] == training["exercise"]["pb"]
            ]
        ),
    }
    return render(request, "trainings_list.html", context)


@login_required
def profile(request):
    if request.method == 'POST':
        form = PasswordChangeCustomForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Votre mot de passe a bien été changé.')
            return redirect('program_builder:profile')
        else:
            messages.error(request, "Corrigez l'erreur s'il vous plait.")
    else:
        form = PasswordChangeCustomForm(request.user)
    user = User.objects.get(pk=request.user.pk)
    context = {'user': user, 'title': 'profile', 'form': form}
    return render(request, "profile.html", context)
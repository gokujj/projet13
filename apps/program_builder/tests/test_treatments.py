#! /usr/bin/env python3
# coding: utf-8
from datetime import datetime
from django.test import TestCase
from django.contrib.auth.models import User

from program_builder.models import (
    Training,
    Exercise,
    MovementsPerExercise,
    MovementSettingsPerMovementsPerExercise,
    Movement,
    MovementSettings,
    Equipment,
)
from program_builder.utils.treatments import DataTreatment
from program_builder.utils.db_interactions import DBMovement
from .helper_dbtestdata import TestDatabase


class TestDataTreatment(TestCase):
    """
    This class tests all the methods from DataTreatment class
    """

    maxDiff = None

    @classmethod
    def setUpTestData(cls):
        """
        Create a database for test with TestDatabase helper
        """
        TestDatabase.create()

    def setUp(self):

        self.treatment = DataTreatment()

    def test_get_all_movements_in_dict(self):
        """
        This test checks if the method get_all_movements_in_dict
        returns an adequate dictionnary
        """

        # We get the movements
        squat = Movement.objects.get(name="squat")
        pushup = Movement.objects.get(name="pushup")
        wallball = Movement.objects.get(name="wallball")
        pullup = Movement.objects.get(name="pullup")

        # We apply the method
        mvts_list = self.treatment.get_all_movements_in_dict()

        # We test
        result = [
            {
                "id": squat.pk,
                "name": squat.name,
                "equipement": squat.equipment.name,
                "settings": [setting.name for setting in squat.settings.all()],
            },
            {
                "id": pushup.pk,
                "name": pushup.name,
                "equipement": pushup.equipment.name,
                "settings": [
                    setting.name for setting in pushup.settings.all()
                ],
            },
            {
                "id": wallball.pk,
                "name": wallball.name,
                "equipement": wallball.equipment.name,
                "settings": [
                    setting.name for setting in wallball.settings.all()
                ],
            },
            {
                "id": pullup.pk,
                "name": pullup.name,
                "equipement": pullup.equipment.name,
                "settings": [
                    setting.name for setting in pullup.settings.all()
                ],
            },
        ]

        self.assertEqual(mvts_list, result)

    def test_register_exercise_from_dict_success(self):
        """
        This test checks if the method register_exercise_from_dict
        registers well the exercise in the database withh all its
        associations.
        """

        # We get the user
        founder = User.objects.get(username="admin_user")

        # We set up some exercise features
        name = "angie"
        exercise_type = "FORTIME"
        description = "workout de test"
        goal_type = "Nombre de tours"
        goal_value = 5

        # We get the movements
        squat = Movement.objects.get(name="squat")
        pushup = Movement.objects.get(name="pushup")
        wallball = Movement.objects.get(name="wallball")

        # We get the settings implicated in the test
        rep = MovementSettings.objects.get(name=MovementSettings.REPETITIONS)
        weight = MovementSettings.objects.get(name=MovementSettings.WEIGHT)

        # We create the dict
        exercise_dict = {
            "name": name,
            "exerciseType": exercise_type,
            "description": description,
            "goalType": goal_type,
            "goalValue": goal_value,
            "movements": [
                {
                    "name": squat.name,
                    "order": 1,
                    "settings": [
                        {
                            "name": "repetitions",
                            "value": 10,
                        },
                        {
                            "name": "poids",
                            "value": 5,
                        },
                    ],
                },
                {
                    "name": pushup.name,
                    "order": 2,
                    "settings": [
                        {
                            "name": "repetitions",
                            "value": 15,
                        },
                    ],
                },
                {
                    "name": wallball.name,
                    "order": 3,
                    "settings": [
                        {
                            "name": "repetitions",
                            "value": 20,
                        },
                        {
                            "name": "poids",
                            "value": 18,
                        },
                    ],
                },
            ],
        }

        # We apply the method
        exercise = self.treatment.register_exercise_from_dict(
            exercise_dict, founder
        )

        # We test
        self.assertEqual(exercise.name, "angie")
        self.assertEqual(exercise.exercise_type, "FORTIME")
        self.assertEqual(exercise.goal_value, 5)
        self.assertEqual(exercise.movements.all().count(), 3)

        angie_squat = MovementsPerExercise.objects.get(
            exercise=exercise, movement=squat
        )
        self.assertEqual(angie_squat.movement_number, 1)
        self.assertEqual(angie_squat.movement_settings.all().count(), 2)

        angie_squat_settings = (
            MovementSettingsPerMovementsPerExercise.objects.filter(
                exercise_movement=angie_squat
            )
        )
        self.assertEqual(angie_squat_settings.count(), 2)
        angie_squat_rep = MovementSettingsPerMovementsPerExercise.objects.get(
            exercise_movement=angie_squat, setting=rep
        )
        self.assertEqual(angie_squat_rep.setting_value, 10)
        angie_squat_weight = (
            MovementSettingsPerMovementsPerExercise.objects.get(
                exercise_movement=angie_squat, setting=weight
            )
        )
        self.assertEqual(angie_squat_weight.setting_value, 5)

        angie_pushup = MovementsPerExercise.objects.get(
            exercise=exercise, movement=pushup
        )
        self.assertEqual(angie_pushup.movement_number, 2)
        self.assertEqual(angie_pushup.movement_settings.all().count(), 1)
        angie_pushup_settings = (
            MovementSettingsPerMovementsPerExercise.objects.filter(
                exercise_movement=angie_pushup
            )
        )
        self.assertEqual(angie_pushup_settings.count(), 1)
        angie_pushup_rep = MovementSettingsPerMovementsPerExercise.objects.get(
            exercise_movement=angie_pushup, setting=rep
        )
        self.assertEqual(angie_pushup_rep.setting_value, 15)

        angie_wallball = MovementsPerExercise.objects.get(
            exercise=exercise, movement=wallball
        )
        self.assertEqual(angie_wallball.movement_number, 3)
        self.assertEqual(angie_wallball.movement_settings.all().count(), 2)

        angie_wallball_settings = (
            MovementSettingsPerMovementsPerExercise.objects.filter(
                exercise_movement=angie_wallball
            )
        )
        self.assertEqual(angie_wallball_settings.count(), 2)
        angie_wallball_rep = (
            MovementSettingsPerMovementsPerExercise.objects.get(
                exercise_movement=angie_wallball, setting=rep
            )
        )
        self.assertEqual(angie_wallball_rep.setting_value, 20)
        angie_wallball_weight = (
            MovementSettingsPerMovementsPerExercise.objects.get(
                exercise_movement=angie_wallball, setting=weight
            )
        )
        self.assertEqual(angie_wallball_weight.setting_value, 18)

    def test_register_exercise_from_dict_success_running_exercise(self):

        # We get the user
        founder = User.objects.get(username="admin_user")

        # We set up some exercise features
        name = "run 7.5"
        exercise_type = "RUNNING"
        description = "running test"
        goal_type = "Distance"
        goal_value = 7.5

        # We create the dict
        exercise_dict = {
            "name": name,
            "exerciseType": exercise_type,
            "description": description,
            "goalType": goal_type,
            "goalValue": goal_value,
            "movements": [],
        }

        # We apply the method
        exercise = self.treatment.register_exercise_from_dict(
            exercise_dict, founder
        )

        # We Test
        self.assertEqual(exercise.name, "run 7.5")
        self.assertEqual(exercise.exercise_type, "RUNNING")
        self.assertEqual(exercise.goal_value, 7500)
        self.assertEqual(exercise.movements.all().count(), 0)

    def test_get_all_exercises_dict_linked_to_one_user(self):
        # We get the user
        admin_founder = User.objects.get(username="admin_user")
        ordinary_founder = User.objects.get(username="ordinary_user")
        new_user = User.objects.get(username="new_user")

        # We get the movements
        pullup = Movement.objects.get(name="pullup")
        pushup = Movement.objects.get(name="pushup")
        squat = Movement.objects.get(name="squat")
        wallball = Movement.objects.get(name="wallball")

        # We get the settings
        rep = MovementSettings.objects.get(name=MovementSettings.REPETITIONS)
        weight = MovementSettings.objects.get(name=MovementSettings.WEIGHT)
        dist = MovementSettings.objects.get(name=MovementSettings.DISTANCE)
        cal = MovementSettings.objects.get(name=MovementSettings.CALORIES)

        # We get the workouts

        # 1. o_chelsea

        o_chelsea = Exercise.objects.get(
            name="chelsea", founder=ordinary_founder
        )
        o_chelsea_pullup = MovementsPerExercise.objects.get(
            exercise=o_chelsea, movement=pullup
        )
        o_chelsea_pullup_rep = (
            MovementSettingsPerMovementsPerExercise.objects.get(
                exercise_movement=o_chelsea_pullup, setting=rep
            )
        )
        o_chelsea_pushup = MovementsPerExercise.objects.get(
            exercise=o_chelsea, movement=pushup
        )
        o_chelsea_pushup_rep = (
            MovementSettingsPerMovementsPerExercise.objects.get(
                exercise_movement=o_chelsea_pushup, setting=rep
            )
        )
        o_chelsea_squat = MovementsPerExercise.objects.get(
            exercise=o_chelsea, movement=squat
        )
        o_chelsea_squat_rep = (
            MovementSettingsPerMovementsPerExercise.objects.get(
                exercise_movement=o_chelsea_squat, setting=rep
            )
        )
        o_chelsea_squat_weight = (
            MovementSettingsPerMovementsPerExercise.objects.get(
                exercise_movement=o_chelsea_squat, setting=weight
            )
        )

        # 2. a_chelsea
        a_chelsea = Exercise.objects.get(name="chelsea", founder=admin_founder)
        a_chelsea_pullup = MovementsPerExercise.objects.get(
            exercise=a_chelsea, movement=pullup
        )
        a_chelsea_pullup_rep = (
            MovementSettingsPerMovementsPerExercise.objects.get(
                exercise_movement=a_chelsea_pullup, setting=rep
            )
        )
        a_chelsea_pushup = MovementsPerExercise.objects.get(
            exercise=a_chelsea, movement=pushup
        )
        a_chelsea_pushup_rep = (
            MovementSettingsPerMovementsPerExercise.objects.get(
                exercise_movement=a_chelsea_pushup, setting=rep
            )
        )
        a_chelsea_squat = MovementsPerExercise.objects.get(
            exercise=a_chelsea, movement=squat
        )
        a_chelsea_squat_rep = (
            MovementSettingsPerMovementsPerExercise.objects.get(
                exercise_movement=a_chelsea_squat, setting=rep
            )
        )
        a_chelsea_squat_weight = (
            MovementSettingsPerMovementsPerExercise.objects.get(
                exercise_movement=a_chelsea_squat, setting=weight
            )
        )

        # 3. connie
        connie = Exercise.objects.get(name="connie", founder=new_user)
        connie_pullup = MovementsPerExercise.objects.get(
            exercise=connie, movement=pullup
        )
        connie_pullup_rep = (
            MovementSettingsPerMovementsPerExercise.objects.get(
                exercise_movement=connie_pullup, setting=rep
            )
        )
        connie_wallball = MovementsPerExercise.objects.get(
            exercise=connie, movement=wallball
        )
        connie_wallball_rep = (
            MovementSettingsPerMovementsPerExercise.objects.get(
                exercise_movement=connie_wallball, setting=rep
            )
        )
        connie_wallball_weight = (
            MovementSettingsPerMovementsPerExercise.objects.get(
                exercise_movement=connie_wallball, setting=weight
            )
        )

        # We get the training

        date = datetime(2018, 3, 8)
        a_chelsea_training = Training.objects.get(
            founder=new_user, exercise=a_chelsea, date=date
        )

        date = datetime(2018, 4, 5)
        connie_first_training = Training.objects.get(
            founder=new_user, exercise=connie, date=date
        )

        date = datetime(2018, 5, 2)
        connie_second_training = Training.objects.get(
            founder=new_user, exercise=connie, date=date
        )

        # Result

        result = [
            {
                "id": a_chelsea_training.exercise.pk,
                "name": a_chelsea_training.exercise.name,
                "exercise_type": a_chelsea_training.exercise.exercise_type,
                "description": a_chelsea_training.exercise.description,
                "goal_type": a_chelsea_training.exercise.goal_type,
                "goal_value": a_chelsea_training.exercise.goal_value,
                "is_default": a_chelsea_training.exercise.is_default,
                "pb": 15,
                "movements": [
                    {
                        "id": a_chelsea_pullup.movement.pk,
                        "name": a_chelsea_pullup.movement.name,
                        "order": a_chelsea_pullup.movement_number,
                        "settings": [
                            {
                                "name": a_chelsea_pullup_rep.setting.name,
                                "value": a_chelsea_pullup_rep.setting_value,
                            },
                        ],
                    },
                    {
                        "id": a_chelsea_pushup.movement.pk,
                        "name": a_chelsea_pushup.movement.name,
                        "order": a_chelsea_pushup.movement_number,
                        "settings": [
                            {
                                "name": a_chelsea_pushup_rep.setting.name,
                                "value": a_chelsea_pushup_rep.setting_value,
                            },
                        ],
                    },
                    {
                        "id": a_chelsea_squat.movement.pk,
                        "name": a_chelsea_squat.movement.name,
                        "order": a_chelsea_squat.movement_number,
                        "settings": [
                            {
                                "name": a_chelsea_squat_rep.setting.name,
                                "value": a_chelsea_squat_rep.setting_value,
                            },
                            {
                                "name": a_chelsea_squat_weight.setting.name,
                                "value": a_chelsea_squat_weight.setting_value,
                            },
                        ],
                    },
                ],
            },
            {
                "id": connie_first_training.exercise.pk,
                "name": connie_first_training.exercise.name,
                "exercise_type": connie_first_training.exercise.exercise_type,
                "description": connie_first_training.exercise.description,
                "goal_type": connie_first_training.exercise.goal_type,
                "goal_value": connie_first_training.exercise.goal_value,
                "is_default": connie_first_training.exercise.is_default,
                "pb": 230,
                "movements": [
                    {
                        "id": connie_pullup.movement.pk,
                        "name": connie_pullup.movement.name,
                        "order": connie_pullup.movement_number,
                        "settings": [
                            {
                                "name": connie_pullup_rep.setting.name,
                                "value": connie_pullup_rep.setting_value,
                            },
                        ],
                    },
                    {
                        "id": connie_wallball.movement.pk,
                        "name": connie_wallball.movement.name,
                        "order": connie_wallball.movement_number,
                        "settings": [
                            {
                                "name": connie_wallball_rep.setting.name,
                                "value": connie_wallball_rep.setting_value,
                            },
                            {
                                "name": connie_wallball_weight.setting.name,
                                "value": connie_wallball_weight.setting_value,
                            },
                        ],
                    },
                ],
            },
        ]

        # We apply the method
        exercises = self.treatment.get_all_exercises_dict_linked_to_one_user(
            new_user
        )

        # We test
        self.assertEqual(exercises, result)

    def test_get_one_exercise_in_dict_linked_to_one_user(self):
        # We get the user
        new_user = User.objects.get(username="new_user")

        # We get the movements
        pullup = Movement.objects.get(name="pullup")
        wallball = Movement.objects.get(name="wallball")

        # We get the settings
        rep = MovementSettings.objects.get(name=MovementSettings.REPETITIONS)
        weight = MovementSettings.objects.get(name=MovementSettings.WEIGHT)

        # We get the workout
        connie = Exercise.objects.get(name="connie", founder=new_user)
        connie_pullup = MovementsPerExercise.objects.get(
            exercise=connie, movement=pullup
        )
        connie_pullup_rep = (
            MovementSettingsPerMovementsPerExercise.objects.get(
                exercise_movement=connie_pullup, setting=rep
            )
        )
        connie_wallball = MovementsPerExercise.objects.get(
            exercise=connie, movement=wallball
        )
        connie_wallball_rep = (
            MovementSettingsPerMovementsPerExercise.objects.get(
                exercise_movement=connie_wallball, setting=rep
            )
        )
        connie_wallball_weight = (
            MovementSettingsPerMovementsPerExercise.objects.get(
                exercise_movement=connie_wallball, setting=weight
            )
        )

        # Result
        result = {
            "id": connie.pk,
            "name": connie.name,
            "exercise_type": connie.exercise_type,
            "description": connie.description,
            "goal_type": connie.goal_type,
            "goal_value": connie.goal_value,
            "is_default": connie.is_default,
            "pb": 230,
            "movements": [
                {
                    "id": connie_pullup.movement.pk,
                    "name": connie_pullup.movement.name,
                    "order": connie_pullup.movement_number,
                    "settings": [
                        {
                            "name": connie_pullup_rep.setting.name,
                            "value": connie_pullup_rep.setting_value,
                        },
                    ],
                },
                {
                    "id": connie_wallball.movement.pk,
                    "name": connie_wallball.movement.name,
                    "order": connie_wallball.movement_number,
                    "settings": [
                        {
                            "name": connie_wallball_rep.setting.name,
                            "value": connie_wallball_rep.setting_value,
                        },
                        {
                            "name": connie_wallball_weight.setting.name,
                            "value": connie_wallball_weight.setting_value,
                        },
                    ],
                },
            ],
        }

        # We test
        connie_dict = (
            self.treatment.get_one_exercise_in_dict_linked_to_one_user(
                connie.pk, new_user
            )
        )
        self.assertEqual(connie_dict, result)

    def test_get_one_training_in_dict_done(self):

        # We get the user
        new_user = User.objects.get(username="new_user")

        # We get the movements
        pullup = Movement.objects.get(name="pullup")
        wallball = Movement.objects.get(name="wallball")

        # We get the settings
        rep = MovementSettings.objects.get(name=MovementSettings.REPETITIONS)
        weight = MovementSettings.objects.get(name=MovementSettings.WEIGHT)

        # We get the workout
        connie = Exercise.objects.get(name="connie", founder=new_user)
        connie_pullup = MovementsPerExercise.objects.get(
            exercise=connie, movement=pullup
        )
        connie_pullup_rep = (
            MovementSettingsPerMovementsPerExercise.objects.get(
                exercise_movement=connie_pullup, setting=rep
            )
        )
        connie_wallball = MovementsPerExercise.objects.get(
            exercise=connie, movement=wallball
        )
        connie_wallball_rep = (
            MovementSettingsPerMovementsPerExercise.objects.get(
                exercise_movement=connie_wallball, setting=rep
            )
        )
        connie_wallball_weight = (
            MovementSettingsPerMovementsPerExercise.objects.get(
                exercise_movement=connie_wallball, setting=weight
            )
        )

        # We get the training
        date = datetime(2018, 4, 5)
        connie_training = Training.objects.get(
            founder=new_user, exercise=connie, date=date
        )

        # We apply the method
        connie_dict = self.treatment.get_one_training_in_dict(
            connie_training.pk, new_user
        )

        # We define the expected result
        result = {
            "id": connie_training.pk,
            "date": connie_training.date,
            "done": connie_training.done,
            "performance_type": connie_training.performance_type,
            "performance_value": connie_training.performance_value,
            "exercise": {
                "id": connie_training.exercise.pk,
                "name": connie_training.exercise.name,
                "exercise_type": connie_training.exercise.exercise_type,
                "description": connie_training.exercise.description,
                "goal_type": connie_training.exercise.goal_type,
                "goal_value": connie_training.exercise.goal_value,
                "is_default": connie_training.exercise.is_default,
                "pb": 230,
                "movements": [
                    {
                        "id": connie_pullup.movement.pk,
                        "name": connie_pullup.movement.name,
                        "order": connie_pullup.movement_number,
                        "settings": [
                            {
                                "name": connie_pullup_rep.setting.name,
                                "value": connie_pullup_rep.setting_value,
                            },
                        ],
                    },
                    {
                        "id": connie_wallball.movement.pk,
                        "name": connie_wallball.movement.name,
                        "order": connie_wallball.movement_number,
                        "settings": [
                            {
                                "name": connie_wallball_rep.setting.name,
                                "value": connie_wallball_rep.setting_value,
                            },
                            {
                                "name": connie_wallball_weight.setting.name,
                                "value": connie_wallball_weight.setting_value,
                            },
                        ],
                    },
                ],
            },
        }

        # We test
        self.assertEqual(connie_dict, result)

    def test_get_one_training_in_dict_not_done(self):
        """
        This test cheks if the method get_one_training_in_dict gets correctly the training
        in dict when any personal best records had been registered yet on the exercise associated
        """
        # We get the users
        admin_founder = User.objects.get(username="admin_user")
        ordinary_user = User.objects.get(username="ordinary_user")

        # We get the movements
        pullup = Movement.objects.get(name="pullup")
        pushup = Movement.objects.get(name="pushup")
        squat = Movement.objects.get(name="squat")

        # We get the settings
        rep = MovementSettings.objects.get(name=MovementSettings.REPETITIONS)
        weight = MovementSettings.objects.get(name=MovementSettings.WEIGHT)

        # We get the workout
        a_chelsea = Exercise.objects.get(name="chelsea", founder=admin_founder)
        a_chelsea_pullup = MovementsPerExercise.objects.get(
            exercise=a_chelsea, movement=pullup
        )
        a_chelsea_pullup_rep = (
            MovementSettingsPerMovementsPerExercise.objects.get(
                exercise_movement=a_chelsea_pullup, setting=rep
            )
        )
        a_chelsea_pushup = MovementsPerExercise.objects.get(
            exercise=a_chelsea, movement=pushup
        )
        a_chelsea_pushup_rep = (
            MovementSettingsPerMovementsPerExercise.objects.get(
                exercise_movement=a_chelsea_pushup, setting=rep
            )
        )
        a_chelsea_squat = MovementsPerExercise.objects.get(
            exercise=a_chelsea, movement=squat
        )
        a_chelsea_squat_rep = (
            MovementSettingsPerMovementsPerExercise.objects.get(
                exercise_movement=a_chelsea_squat, setting=rep
            )
        )
        a_chelsea_squat_weight = (
            MovementSettingsPerMovementsPerExercise.objects.get(
                exercise_movement=a_chelsea_squat, setting=weight
            )
        )

        # We get the training
        date = datetime(2018, 8, 8)
        a_chelsea_training = Training.objects.get(
            founder=ordinary_user, exercise=a_chelsea, date=date
        )

        # We apply the method
        a_chelsea_dict = self.treatment.get_one_training_in_dict(
            a_chelsea_training.pk, ordinary_user
        )

        # We define the expected result
        result = {
            "id": a_chelsea_training.pk,
            "date": a_chelsea_training.date,
            "done": a_chelsea_training.done,
            "performance_type": a_chelsea_training.performance_type,
            "performance_value": a_chelsea_training.performance_value,
            "exercise": {
                "id": a_chelsea_training.exercise.pk,
                "name": a_chelsea_training.exercise.name,
                "exercise_type": a_chelsea_training.exercise.exercise_type,
                "description": a_chelsea_training.exercise.description,
                "goal_type": a_chelsea_training.exercise.goal_type,
                "goal_value": a_chelsea_training.exercise.goal_value,
                "is_default": a_chelsea_training.exercise.is_default,
                "pb": 0,
                "movements": [
                    {
                        "id": a_chelsea_pullup.movement.pk,
                        "name": a_chelsea_pullup.movement.name,
                        "order": a_chelsea_pullup.movement_number,
                        "settings": [
                            {
                                "name": a_chelsea_pullup_rep.setting.name,
                                "value": a_chelsea_pullup_rep.setting_value,
                            },
                        ],
                    },
                    {
                        "id": a_chelsea_pushup.movement.pk,
                        "name": a_chelsea_pushup.movement.name,
                        "order": a_chelsea_pushup.movement_number,
                        "settings": [
                            {
                                "name": a_chelsea_pushup_rep.setting.name,
                                "value": a_chelsea_pushup_rep.setting_value,
                            },
                        ],
                    },
                    {
                        "id": a_chelsea_squat.movement.pk,
                        "name": a_chelsea_squat.movement.name,
                        "order": a_chelsea_squat.movement_number,
                        "settings": [
                            {
                                "name": a_chelsea_squat_rep.setting.name,
                                "value": a_chelsea_squat_rep.setting_value,
                            },
                            {
                                "name": a_chelsea_squat_weight.setting.name,
                                "value": a_chelsea_squat_weight.setting_value,
                            },
                        ],
                    },
                ],
            },
        }

        # We test
        self.assertEqual(a_chelsea_dict, result)

    def test_get_all_trainings_per_user_in_dict(self):
        """
        This test checks if the method get_all_trainings_per_user_in_dict
        gets the correct trainings
        """

        # We get the user
        admin_founder = User.objects.get(username="admin_user")
        ordinary_founder = User.objects.get(username="ordinary_user")
        new_user = User.objects.get(username="new_user")

        # We get the movements
        pullup = Movement.objects.get(name="pullup")
        pushup = Movement.objects.get(name="pushup")
        squat = Movement.objects.get(name="squat")
        wallball = Movement.objects.get(name="wallball")

        # We get the settings
        rep = MovementSettings.objects.get(name=MovementSettings.REPETITIONS)
        weight = MovementSettings.objects.get(name=MovementSettings.WEIGHT)
        dist = MovementSettings.objects.get(name=MovementSettings.DISTANCE)
        cal = MovementSettings.objects.get(name=MovementSettings.CALORIES)

        # We get the workouts

        # 1. o_chelsea

        o_chelsea = Exercise.objects.get(
            name="chelsea", founder=ordinary_founder
        )
        o_chelsea_pullup = MovementsPerExercise.objects.get(
            exercise=o_chelsea, movement=pullup
        )
        o_chelsea_pullup_rep = (
            MovementSettingsPerMovementsPerExercise.objects.get(
                exercise_movement=o_chelsea_pullup, setting=rep
            )
        )
        o_chelsea_pushup = MovementsPerExercise.objects.get(
            exercise=o_chelsea, movement=pushup
        )
        o_chelsea_pushup_rep = (
            MovementSettingsPerMovementsPerExercise.objects.get(
                exercise_movement=o_chelsea_pushup, setting=rep
            )
        )
        o_chelsea_squat = MovementsPerExercise.objects.get(
            exercise=o_chelsea, movement=squat
        )
        o_chelsea_squat_rep = (
            MovementSettingsPerMovementsPerExercise.objects.get(
                exercise_movement=o_chelsea_squat, setting=rep
            )
        )
        o_chelsea_squat_weight = (
            MovementSettingsPerMovementsPerExercise.objects.get(
                exercise_movement=o_chelsea_squat, setting=weight
            )
        )

        # 2. a_chelsea
        a_chelsea = Exercise.objects.get(name="chelsea", founder=admin_founder)
        a_chelsea_pullup = MovementsPerExercise.objects.get(
            exercise=a_chelsea, movement=pullup
        )
        a_chelsea_pullup_rep = (
            MovementSettingsPerMovementsPerExercise.objects.get(
                exercise_movement=a_chelsea_pullup, setting=rep
            )
        )
        a_chelsea_pushup = MovementsPerExercise.objects.get(
            exercise=a_chelsea, movement=pushup
        )
        a_chelsea_pushup_rep = (
            MovementSettingsPerMovementsPerExercise.objects.get(
                exercise_movement=a_chelsea_pushup, setting=rep
            )
        )
        a_chelsea_squat = MovementsPerExercise.objects.get(
            exercise=a_chelsea, movement=squat
        )
        a_chelsea_squat_rep = (
            MovementSettingsPerMovementsPerExercise.objects.get(
                exercise_movement=a_chelsea_squat, setting=rep
            )
        )
        a_chelsea_squat_weight = (
            MovementSettingsPerMovementsPerExercise.objects.get(
                exercise_movement=a_chelsea_squat, setting=weight
            )
        )

        # 3. connie
        connie = Exercise.objects.get(name="connie", founder=new_user)
        connie_pullup = MovementsPerExercise.objects.get(
            exercise=connie, movement=pullup
        )
        connie_pullup_rep = (
            MovementSettingsPerMovementsPerExercise.objects.get(
                exercise_movement=connie_pullup, setting=rep
            )
        )
        connie_wallball = MovementsPerExercise.objects.get(
            exercise=connie, movement=wallball
        )
        connie_wallball_rep = (
            MovementSettingsPerMovementsPerExercise.objects.get(
                exercise_movement=connie_wallball, setting=rep
            )
        )
        connie_wallball_weight = (
            MovementSettingsPerMovementsPerExercise.objects.get(
                exercise_movement=connie_wallball, setting=weight
            )
        )

        # We get the training

        date = datetime(2018, 3, 8)
        a_chelsea_training = Training.objects.get(
            founder=new_user, exercise=a_chelsea, date=date
        )

        date = datetime(2018, 4, 5)
        connie_first_training = Training.objects.get(
            founder=new_user, exercise=connie, date=date
        )

        date = datetime(2018, 5, 2)
        connie_second_training = Training.objects.get(
            founder=new_user, exercise=connie, date=date
        )

        # Result

        result = [
            {
                "id": connie_second_training.pk,
                "date": connie_second_training.date,
                "done": connie_second_training.done,
                "performance_type": connie_second_training.performance_type,
                "performance_value": connie_second_training.performance_value,
                "exercise": {
                    "id": connie_second_training.exercise.pk,
                    "name": connie_second_training.exercise.name,
                    "exercise_type": connie_second_training.exercise.exercise_type,
                    "description": connie_second_training.exercise.description,
                    "goal_type": connie_second_training.exercise.goal_type,
                    "goal_value": connie_second_training.exercise.goal_value,
                    "is_default": connie_second_training.exercise.is_default,
                    "pb": 230,
                    "movements": [
                        {
                            "id": connie_pullup.movement.pk,
                            "name": connie_pullup.movement.name,
                            "order": connie_pullup.movement_number,
                            "settings": [
                                {
                                    "name": connie_pullup_rep.setting.name,
                                    "value": connie_pullup_rep.setting_value,
                                },
                            ],
                        },
                        {
                            "id": connie_wallball.movement.pk,
                            "name": connie_wallball.movement.name,
                            "order": connie_wallball.movement_number,
                            "settings": [
                                {
                                    "name": connie_wallball_rep.setting.name,
                                    "value": connie_wallball_rep.setting_value,
                                },
                                {
                                    "name": connie_wallball_weight.setting.name,
                                    "value": connie_wallball_weight.setting_value,
                                },
                            ],
                        },
                    ],
                },
            },
            {
                "id": connie_first_training.pk,
                "date": connie_first_training.date,
                "done": connie_first_training.done,
                "performance_type": connie_first_training.performance_type,
                "performance_value": connie_first_training.performance_value,
                "exercise": {
                    "id": connie_first_training.exercise.pk,
                    "name": connie_first_training.exercise.name,
                    "exercise_type": connie_first_training.exercise.exercise_type,
                    "description": connie_first_training.exercise.description,
                    "goal_type": connie_first_training.exercise.goal_type,
                    "goal_value": connie_first_training.exercise.goal_value,
                    "is_default": connie_first_training.exercise.is_default,
                    "pb": 230,
                    "movements": [
                        {
                            "id": connie_pullup.movement.pk,
                            "name": connie_pullup.movement.name,
                            "order": connie_pullup.movement_number,
                            "settings": [
                                {
                                    "name": connie_pullup_rep.setting.name,
                                    "value": connie_pullup_rep.setting_value,
                                },
                            ],
                        },
                        {
                            "id": connie_wallball.movement.pk,
                            "name": connie_wallball.movement.name,
                            "order": connie_wallball.movement_number,
                            "settings": [
                                {
                                    "name": connie_wallball_rep.setting.name,
                                    "value": connie_wallball_rep.setting_value,
                                },
                                {
                                    "name": connie_wallball_weight.setting.name,
                                    "value": connie_wallball_weight.setting_value,
                                },
                            ],
                        },
                    ],
                },
            },
            {
                "id": a_chelsea_training.pk,
                "date": a_chelsea_training.date,
                "done": a_chelsea_training.done,
                "performance_type": a_chelsea_training.performance_type,
                "performance_value": a_chelsea_training.performance_value,
                "exercise": {
                    "id": a_chelsea_training.exercise.pk,
                    "name": a_chelsea_training.exercise.name,
                    "exercise_type": a_chelsea_training.exercise.exercise_type,
                    "description": a_chelsea_training.exercise.description,
                    "goal_type": a_chelsea_training.exercise.goal_type,
                    "goal_value": a_chelsea_training.exercise.goal_value,
                    "is_default": a_chelsea_training.exercise.is_default,
                    "pb": 15,
                    "movements": [
                        {
                            "id": a_chelsea_pullup.movement.pk,
                            "name": a_chelsea_pullup.movement.name,
                            "order": a_chelsea_pullup.movement_number,
                            "settings": [
                                {
                                    "name": a_chelsea_pullup_rep.setting.name,
                                    "value": a_chelsea_pullup_rep.setting_value,
                                },
                            ],
                        },
                        {
                            "id": a_chelsea_pushup.movement.pk,
                            "name": a_chelsea_pushup.movement.name,
                            "order": a_chelsea_pushup.movement_number,
                            "settings": [
                                {
                                    "name": a_chelsea_pushup_rep.setting.name,
                                    "value": a_chelsea_pushup_rep.setting_value,
                                },
                            ],
                        },
                        {
                            "id": a_chelsea_squat.movement.pk,
                            "name": a_chelsea_squat.movement.name,
                            "order": a_chelsea_squat.movement_number,
                            "settings": [
                                {
                                    "name": a_chelsea_squat_rep.setting.name,
                                    "value": a_chelsea_squat_rep.setting_value,
                                },
                                {
                                    "name": a_chelsea_squat_weight.setting.name,
                                    "value": a_chelsea_squat_weight.setting_value,
                                },
                            ],
                        },
                    ],
                },
            },
        ]

        # We apply the method
        trainings = self.treatment.get_all_trainings_per_user_in_dict(new_user)

        # We test
        self.assertEqual(trainings, result)

    def test_get_all_trainings_per_user_linked_to_an_exercise(self):
        """
        This test checks if the method get_all_trainings_per_user_linked_to_an_exercise
        gets the correct trainings
        """
        # We get the user
        new_user = User.objects.get(username="new_user")

        # We get the movements
        pullup = Movement.objects.get(name="pullup")
        wallball = Movement.objects.get(name="wallball")

        # We get the settings
        rep = MovementSettings.objects.get(name=MovementSettings.REPETITIONS)
        weight = MovementSettings.objects.get(name=MovementSettings.WEIGHT)

        # We get the workout

        connie = Exercise.objects.get(name="connie", founder=new_user)
        connie_pullup = MovementsPerExercise.objects.get(
            exercise=connie, movement=pullup
        )
        connie_pullup_rep = (
            MovementSettingsPerMovementsPerExercise.objects.get(
                exercise_movement=connie_pullup, setting=rep
            )
        )
        connie_wallball = MovementsPerExercise.objects.get(
            exercise=connie, movement=wallball
        )
        connie_wallball_rep = (
            MovementSettingsPerMovementsPerExercise.objects.get(
                exercise_movement=connie_wallball, setting=rep
            )
        )
        connie_wallball_weight = (
            MovementSettingsPerMovementsPerExercise.objects.get(
                exercise_movement=connie_wallball, setting=weight
            )
        )

        # We get the training

        date = datetime(2018, 4, 5)
        connie_first_training = Training.objects.get(
            founder=new_user, exercise=connie, date=date
        )

        date = datetime(2018, 5, 2)
        connie_second_training = Training.objects.get(
            founder=new_user, exercise=connie, date=date
        )

        result = [
            {
                "id": connie_second_training.pk,
                "date": connie_second_training.date,
                "done": connie_second_training.done,
                "performance_type": connie_second_training.performance_type,
                "performance_value": connie_second_training.performance_value,
                "exercise": {
                    "id": connie_second_training.exercise.pk,
                    "name": connie_second_training.exercise.name,
                    "exercise_type": connie_second_training.exercise.exercise_type,
                    "description": connie_second_training.exercise.description,
                    "goal_type": connie_second_training.exercise.goal_type,
                    "goal_value": connie_second_training.exercise.goal_value,
                    "is_default": connie_second_training.exercise.is_default,
                    "pb": 230,
                    "movements": [
                        {
                            "id": connie_pullup.movement.pk,
                            "name": connie_pullup.movement.name,
                            "order": connie_pullup.movement_number,
                            "settings": [
                                {
                                    "name": connie_pullup_rep.setting.name,
                                    "value": connie_pullup_rep.setting_value,
                                },
                            ],
                        },
                        {
                            "id": connie_wallball.movement.pk,
                            "name": connie_wallball.movement.name,
                            "order": connie_wallball.movement_number,
                            "settings": [
                                {
                                    "name": connie_wallball_rep.setting.name,
                                    "value": connie_wallball_rep.setting_value,
                                },
                                {
                                    "name": connie_wallball_weight.setting.name,
                                    "value": connie_wallball_weight.setting_value,
                                },
                            ],
                        },
                    ],
                },
            },
            {
                "id": connie_first_training.pk,
                "date": connie_first_training.date,
                "done": connie_first_training.done,
                "performance_type": connie_first_training.performance_type,
                "performance_value": connie_first_training.performance_value,
                "exercise": {
                    "id": connie_first_training.exercise.pk,
                    "name": connie_first_training.exercise.name,
                    "exercise_type": connie_first_training.exercise.exercise_type,
                    "description": connie_first_training.exercise.description,
                    "goal_type": connie_first_training.exercise.goal_type,
                    "goal_value": connie_first_training.exercise.goal_value,
                    "is_default": connie_first_training.exercise.is_default,
                    "pb": 230,
                    "movements": [
                        {
                            "id": connie_pullup.movement.pk,
                            "name": connie_pullup.movement.name,
                            "order": connie_pullup.movement_number,
                            "settings": [
                                {
                                    "name": connie_pullup_rep.setting.name,
                                    "value": connie_pullup_rep.setting_value,
                                },
                            ],
                        },
                        {
                            "id": connie_wallball.movement.pk,
                            "name": connie_wallball.movement.name,
                            "order": connie_wallball.movement_number,
                            "settings": [
                                {
                                    "name": connie_wallball_rep.setting.name,
                                    "value": connie_wallball_rep.setting_value,
                                },
                                {
                                    "name": connie_wallball_weight.setting.name,
                                    "value": connie_wallball_weight.setting_value,
                                },
                            ],
                        },
                    ],
                },
            },
        ]

        # We apply the method
        trainings = (
            self.treatment.get_all_trainings_per_user_linked_to_an_exercise(
                connie, new_user
            )
        )

        # We test
        self.assertEqual(trainings, result)
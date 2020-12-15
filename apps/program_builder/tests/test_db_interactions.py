#! /usr/bin/env python3
# coding: utf-8
from django.test import TestCase
from django.contrib.auth.models import User
from django.db.models import Q

from program_builder.models import (
    Training,
    Exercise,
    MovementsPerExercise,
    Movement,
    MovementSettings,
    Equipment,
    MovementSettingsPerMovementsPerExercise,
)
from program_builder.utils.db_interactions import (
    DBMovement,
    DBExercise,
    DBTraining,
)
from .helper_dbtestdata import TestDatabase


class TestDBMovement(TestCase):
    """
    This class tests all the methods
    from DBMovement
    """

    @classmethod
    def setUpTestData(cls):
        """
        Create a database for test with TestDatabase helper
        """
        TestDatabase.create()

    def setUp(self):
        self.db_mvt = DBMovement()
        self.db_exo = DBExercise()

    def test_set_settings_movement_one_setting_success(self):
        """
        This test check the method register well one setting
        """

        movement = Movement.objects.get(name="squat")
        cal = MovementSettings.objects.get(name=MovementSettings.CALORIES)

        # Two are already associated in the database test
        self.assertEqual(movement.settings.all().count(), 2)
        movement_settings = self.db_mvt.set_settings_to_movement(movement, cal)
        self.assertEqual(movement.settings.all().count(), 3)

    def test_set_settings_movement_several_settings_success(self):
        """
        This test check the method register well several settings
        """

        movement = Movement.objects.get(name="squat")
        cal = MovementSettings.objects.get(name=MovementSettings.CALORIES)
        dist = MovementSettings.objects.get(name=MovementSettings.DISTANCE)

        # Two are already associated in the database test
        self.assertEqual(movement.settings.all().count(), 2)
        movement_settings = self.db_mvt.set_settings_to_movement(
            movement, cal, dist
        )
        self.assertEqual(movement.settings.all().count(), 4)

    def test_set_settings_movement_setting_already_exists(self):
        """
        This test check the method register well several settings even if several of them
        are already associated
        """

        movement = Movement.objects.get(name="squat")
        cal = MovementSettings.objects.get(name=MovementSettings.CALORIES)
        dist = MovementSettings.objects.get(name=MovementSettings.DISTANCE)
        rep = MovementSettings.objects.get(name=MovementSettings.REPETITIONS)
        weight = MovementSettings.objects.get(name=MovementSettings.WEIGHT)

        # Two are already associated in the database test
        self.assertEqual(movement.settings.all().count(), 2)
        movement_settings = self.db_mvt.set_settings_to_movement(
            movement, cal, dist, rep, weight
        )
        self.assertEqual(movement.settings.all().count(), 4)


class TestDBExercise(TestCase):
    """
    This class tests all the methods
    from DBExercise
    """

    @classmethod
    def setUpTestData(cls):
        """
        Create a database for test with TestDatabase helper
        """
        TestDatabase.create()

    def setUp(self):
        self.db_exo = DBExercise()

    def test_define_goal_type(self):
        """
        This test only checks if the method _define_performance_type associates correctly
        the exercise_type with the adequate performance_type
        """

        goal_type = self.db_exo._define_goal_type('AMRAP')
        self.assertEqual(goal_type, 'duree')

        goal_type = self.db_exo._define_goal_type('EMOM')
        self.assertEqual(goal_type, 'duree')

        goal_type = self.db_exo._define_goal_type('RUNNING')
        self.assertEqual(goal_type, 'distance')

        goal_type = self.db_exo._define_goal_type('FORTIME')
        self.assertEqual(goal_type, 'round')

        goal_type = self.db_exo._define_goal_type('ECHAUFFEMENT')
        self.assertEqual(goal_type, 'round')

        goal_type = self.db_exo._define_goal_type('FORCE')
        self.assertEqual(goal_type, 'round')

        goal_type = self.db_exo._define_goal_type('CONDITIONNEMENT')
        self.assertEqual(goal_type, 'round')

    def test_set_exercise_success(self):
        """
        This test checks if the method set_exercise registers well
        a new exercise
        """

        exercise_name = 'Angie'
        exercise_type = "RUNNING"
        description = "test exo"
        goal_type = "Distance"
        goal_value = "8000"
        founder = User.objects.get(username='admin_user')

        exercise = self.db_exo.set_exercise(
            exercise_name,
            exercise_type,
            description,
            goal_type,
            goal_value,
            founder,
        )

        exercise_exists = Exercise.objects.filter(name=exercise_name).exists()
        self.assertTrue(exercise_exists)

        exercise_registered = Exercise.objects.get(name=exercise_name)
        self.assertEqual(exercise_registered.name, 'Angie')
        self.assertEqual(exercise_registered.exercise_type, 'RUNNING')
        self.assertEqual(exercise_registered.goal_type, 'distance')

    def test_set_movement_to_exercise_success(self):
        """
        This test checks if the method set_exercise registers well a new
        movement to an exercise
        """

        # We get the user
        founder = User.objects.get(username='admin_user')

        # We get an exercise
        connie = Exercise.objects.get(name="connie")

        # We get one movement
        pushup = Movement.objects.get(name="pushup")

        # Connie workout has two movements associated before new association
        self.assertEqual(connie.movements.all().count(), 2)
        # We associate the movement as a third movements for connie workout
        connie_pushup = self.db_exo.set_movement_to_exercise(connie, pushup, 3)

        # We test
        self.assertEqual(connie.movements.all().count(), 3)
        self.assertEqual(connie_pushup.movement_number, 3)

    def test_set_settings_value_to_movement_linked_to_exercise_success(self):
        """
        This method tests the method set_settings_value_to_movement_linked_to_exercise
        """

        # We get the user
        founder = User.objects.get(username='admin_user')

        # We get an exercise
        connie = Exercise.objects.get(name="connie")

        # We get a setting
        rep = MovementSettings.objects.get(name=MovementSettings.REPETITIONS)

        # We get one movement
        pushup = Movement.objects.get(name="pushup")

        # We associate the movement as a third movements for connie workout
        connie_pushup = self.db_exo.set_movement_to_exercise(connie, pushup, 3)

        # We associate a number of repetitions of pushup for connie workout
        rep_value = (
            self.db_exo.set_settings_value_to_movement_linked_to_exercise(
                connie_pushup, rep, 10
            )
        )

        # We test
        self.assertEqual(rep_value.setting_value, 10)
        self.assertEqual(rep_value.setting, rep)
        self.assertEqual(rep_value.exercise_movement.exercise, connie)
        self.assertEqual(rep_value.exercise_movement.movement, pushup)


class TestDBTraining(TestCase):
    """
    This class tests all the methods
    from DBTraining
    """

    @classmethod
    def setUpTestData(cls):
        """
        Create a database for test with TestDatabase helper
        """
        TestDatabase.create()

    def setUp(self):
        self.db_training = DBTraining()

    def test_set_training_success(self):
        """
        This method tests the set_training method
        """
        # We get a founder
        founder = User.objects.get(username="ordinary_user")
        # We get an exercise
        chelsea = Exercise.objects.get(name="chelsea", founder=founder)

        # We apply the method
        training = self.db_training.set_training(chelsea, founder)

        # We test
        self.assertEqual(training.performance_type, Training.ROUND)
        self.assertEqual(training.exercise.name, chelsea.name)
        self.assertFalse(training.done)

    def test_get_all_trainings_from_one_user(self):
        """
        This test checks if the method get all trainings from one user works
        well
        """
        # We get the founder
        founder = User.objects.get(username="new_user")

        # We apply the method
        trainings = self.db_training.get_all_trainings_from_one_user(founder)

        # We test
        self.assertEqual(trainings.count(), 3)

    def test_get_all_trainings_from_one_user_from_one_exercise(self):
        """
        This test checks if the method get_all_trainings_from_one_user_from_one_exercise
        works well
        """
        # We get the founder
        founder = User.objects.get(username="new_user")

        # We get the exercise
        connie = Exercise.objects.get(name="connie")

        # We apply the method
        trainings = (
            self.db_training.get_all_trainings_from_one_user_from_one_exercise(
                connie, founder
            )
        )

        # We test
        self.assertEqual(trainings.count(), 2)
#! /usr/bin/env python3
# coding: utf-8
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from .helper_dbtestdata import TestDatabase
from ..utils.db_interactions import DBMovement
from ..models import (
    Training,
    Exercise,
    MovementsPerExercise,
    MovementSettingsPerMovementsPerExercise,
    Movement,
    MovementSettings,
    Equipment,
)


class IndexPageTestCase(TestCase):
    """
    This class tests the index view
    """

    @classmethod
    def setUpTestData(cls):
        username = 'user'
        user = User.objects.create_user(username=username)
        user.set_password('test-view')
        user.save()

    def test_index_when_logged(self):
        self.client.login(username='user', password='test-view')
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/app/trainings/')

    def test_index_when_not_logged(self):
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/users/login/')


class AjaxAllMovementsPageTestCase(TestCase):
    """
    This class tests the ajax_all_movements view
    """

    @classmethod
    def setUpTestData(cls):
        username = 'user'
        user = User.objects.create_user(username=username)
        user.set_password('test-view')
        user.save()

    def test_movements_list_page_page_when_logged(self):
        self.client.login(username='user', password='test-view')
        response = self.client.get(
            reverse('program_builder:ajax_all_movements')
        )
        self.assertEqual(response.status_code, 200)

    def test_movements_list_page_page_when_not_logged(self):
        response = self.client.get(
            reverse('program_builder:ajax_all_movements')
        )
        self.assertEqual(response.status_code, 302)


class ExercisesListPageTestCase(TestCase):
    """
    This class tests the exercises_list view
    """

    @classmethod
    def setUpTestData(cls):
        username = 'user'
        user = User.objects.create_user(username=username)
        user.set_password('test-view')
        user.save()

    def test_exercises_list_page_when_logged(self):
        self.client.login(username='user', password='test-view')
        response = self.client.get(reverse('program_builder:exercises_list'))
        self.assertEqual(response.status_code, 200)

    def test_exercises_list_page_when_not_logged(self):
        response = self.client.get(reverse('program_builder:exercises_list'))
        self.assertEqual(response.status_code, 302)


class ExercisePageTestCase(TestCase):
    """
    This class tests the exercise page view
    """

    @classmethod
    def setUpTestData(cls):
        """
        Create a database for test with TestDatabase helper
        """
        TestDatabase.create()

    def test_exercise_page_when_logged(self):
        user = User.objects.get(username='ordinary_user')
        self.client.login(username='ordinary_user', password='ordinary_user')
        o_chelsea_exercise = Exercise.objects.get(name="chelsea", founder=user)
        response = self.client.get(
            reverse(
                'program_builder:exercise_page', args=(o_chelsea_exercise.pk,)
            )
        )
        self.assertEqual(response.status_code, 200)

    def test_exercise_page_when_not_logged(self):
        user = User.objects.get(username='ordinary_user')
        o_chelsea_exercise = Exercise.objects.get(name="chelsea", founder=user)
        response = self.client.get(
            reverse(
                'program_builder:exercise_page', args=(o_chelsea_exercise.pk,)
            )
        )
        self.assertEqual(response.status_code, 302)


class TrainingsListTestCase(TestCase):
    """
    This class tests the trainings list view
    """

    @classmethod
    def setUpTestData(cls):
        username = 'user'
        user = User.objects.create_user(username=username)
        user.set_password('test-view')
        user.save()

    def test_exercises_list_page_when_logged(self):
        self.client.login(username='user', password='test-view')
        response = self.client.get(reverse('program_builder:trainings_list'))
        self.assertEqual(response.status_code, 200)

    def test_exercises_list_page_when_not_logged(self):
        response = self.client.get(reverse('program_builder:trainings_list'))
        self.assertEqual(response.status_code, 302)


class ProfileTestCase(TestCase):
    """
    This class tests the profile page view
    """

    @classmethod
    def setUpTestData(cls):
        username = 'user'
        user = User.objects.create_user(username=username)
        user.set_password('test-view')
        user.save()

    def test_exercises_list_page_when_logged(self):
        self.client.login(username='user', password='test-view')
        response = self.client.get(reverse('program_builder:profile'))
        self.assertEqual(response.status_code, 200)

    def test_exercises_list_page_when_not_logged(self):
        response = self.client.get(reverse('program_builder:profile'))
        self.assertEqual(response.status_code, 302)
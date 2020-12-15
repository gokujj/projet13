#! /usr/bin/env python3
# coding: utf-8
from django.db.models import Q
from django.contrib.auth.models import User
from ..models import Training, Exercise, MovementsPerExercise, MovementSettingsPerMovementsPerExercise, Movement, MovementSettings, Equipment

class DBMovement:
    """
    This class manages all the interactions with the database concerning Movement:
        - all set_* methods register data in the database
        - all get_* methods get data from the database
        - all change_* methods modify information in the database
        - all del_* methods delete information from the database
    """

    def set_movement(self, movement_name, founder, equipment):
        """
        This method registers and returns a movement only if it does not already exist
        in the database.
        If the movement already exists, it returns the string "already_exists"
        To create a movement, the argument used must have been created before:
            - founder
            - equipment
        """

        try:
            movement = Movement.objects.create(name=movement_name.lower(),
                                               founder=founder,
                                               equipment=equipment)
            return movement
        except:
            return None

    def set_settings_to_movement(self, movement, *settings):
        """
        This method associates and returns movement settings to a movement if the 
        setting is not already associated in the database.
        To associate one or several settings to a movement, the movement must have
        been created before
        """
        
        movement_settings = movement.settings.all()
        for setting in settings:
            if setting not in movement_settings:
                movement.settings.add(setting)
        return movement.settings.all()

    def get_all_movements(self):
        """
        This simple method returns all the movements registered in the database
        """
        return Movement.objects.all()

    def get_one_movement(self, name):
        """
        This simple method returns one movement according its name
        """
        return Movement.objects.get(name=name)

    def del_movement(self, movement_pk):
        """
        This method deletes a movement only if the movement is not associated
        to an exercise
        NEED TO BE IMPROVED TO MANAGE THE CASE WHERE THE MOVEMENT IS ASSOCIATED
        TO ONE OR SEVERAL EXERCISE
        """
        
        return Movement.objects.get(pk=movement_pk).delete()

    def get_one_movement_setting(self, name):

        return MovementSettings.objects.get(name=name)

class DBExercise:
    """
    This class manages all the interactions with the database concerning Exercise:
        - all set_* methods register data in the database
        - all get_* methods get data from the database
        - all change_* methods modify information in the database
        - all del_* methods delete information from the database
    """

    def _define_goal_type(self, exercise_type):
        """
        This method defines the adequate value of performance type accoding
        the exercise type (see possibilities in model Exercise)
        """
        goal_type = ''
        if exercise_type == 'RUNNING':
            goal_type = 'distance'
        elif exercise_type == 'AMRAP' or exercise_type == "EMOM":
            goal_type = 'duree'
        else:
            goal_type = 'round'
        return goal_type


    def set_exercise(self, exercise_name, exercise_type, description, goal_type, goal_value, founder):
        """
        This method creates and returns an exercise.
        To create an exercise, the argument used must have been created before:
            - the founder
        """

        goal_type = self._define_goal_type(exercise_type)
        exercise = Exercise.objects.create(name=exercise_name, 
                                            exercise_type=exercise_type,
                                            description=description,
                                            goal_type=goal_type,
                                            goal_value=goal_value,
                                            founder=founder)

        if founder.is_superuser:
            exercise.is_default = True
            exercise.save()
            
        return exercise

    def set_movement_to_exercise(self, exercise, movement, movement_number):
        """
        This method associates and returns movements to an exercise.
        To associate one or several settings to a movement, the movement must have been created before
        We need to associate an order to a movement to hierarchize the different movements inside the exercise.
        During this process, the order is added automatically. We take the number of movements already added to
        the identified exercise and we add +1.
        Thanks to this, we are sure at the moment of the creation that two different movements won't have the
        same movement_number(= order)
        """

        movement_exercise = MovementsPerExercise.objects.create(exercise=exercise,
                                                                movement=movement,
                                                                movement_number=movement_number)
        
        return movement_exercise

    def set_settings_value_to_movement_linked_to_exercise(self, exercise_movement, setting, setting_value):
        """
        This method organizes and defines value for movement settings for an identified movement
        associated to an identified exercise
        """
        exercise_movement = MovementSettingsPerMovementsPerExercise.objects.create(exercise_movement=exercise_movement,
                                                                setting=setting,
                                                                setting_value=setting_value)
        
        return exercise_movement


    def get_all_exercises(self):

        return Exercise.objects.all()

    def get_all_default_exercises(self):
        """
        Gets all the exercise created by an administrator
        TO TEST
        """

        return Exercise.objects.filter(is_default=True)

    def get_all_user_exercises(self, user):
        """
        Gets all the exercises created by a user + the default exercise
        TO TEST
        """

        return Exercise.objects.filter(Q(founder=user) | Q(is_default=True))

    def get_one_exercise_by_pk(self, exercise_pk):

        return Exercise.objects.get(pk=exercise_pk)

    def del_exercise(self, exercise_pk):
        """
        This method deletes an exercise only if the exercise is not associated
        to a training
        NEED TO BE IMPROVED TO MANAGE THE CASE WHERE THE EXERCISE IS ASSOCIATED
        TO ONE OR SEVERAL TRAININGS
        """
        
        return Exercise.objects.get(pk=exercise_pk).delete()

    def get_all_movements_linked_to_exercise(self, exercise):
        """
        NO TEST YET
        """
        
        return MovementsPerExercise.objects.filter(exercise=exercise)

    def get_all_settings_linked_to_movement_linked_to_exercise(self, movement_linked):
        """
        NO TEST YET
        """

        return MovementSettingsPerMovementsPerExercise.objects.filter(exercise_movement=movement_linked)

class DBTraining:

    def set_training(self, exercise, founder):
        """
        This method set a training from an exercise
        """

        performance_type = self._set_performance_type(exercise)
        training = Training.objects.create(exercise=exercise,
                                            founder=founder,
                                            performance_type=performance_type)

        return training

    def _set_performance_type(self, exercise):
        """
        This method defines the performance type for a training
        according to the exercise type of the associated exercise
        """

        performance_type = ""
        if exercise.exercise_type == Exercise.FORTIME or exercise.exercise_type == Exercise.RUNNING:
            performance_type = Training.TIME
        elif exercise.exercise_type == Exercise.AMRAP or exercise.exercise_type == Exercise.EMOM:
            performance_type = Training.ROUND
        else:
            performance_type = Training.ANYONE

        return performance_type

    def get_all_trainings_from_one_user(self, user):
        """
        This method gets all the trainings from one user in the database
        """
        
        return Training.objects.filter(founder=user).order_by('-date')
    
    def get_all_trainings_from_one_user_from_one_exercise(self, exercise, user):
        """
        This method gets all the trainings from one user in the database linked
        to a specific exercise
        """
        
        return Training.objects.filter(exercise=exercise, founder=user).order_by('-date')

    def get_one_training_from_pk(self, training_pk):

        return Training.objects.get(pk=training_pk)

class DBInteractions:
    """
    This class manages all the interactions with the database:
        - all set_* methods register data in the database
        - all get_* methods get data from the database
        - all change_* methods modify information in the database
        - all del_* methods delete information from the database
    """

    ## SET METHODS ##

    # Maybe set this methods in auth app
    def set_profile(self):
        pass

    def set_training(self):
        pass

    def set_exercise_to_training(self):
        pass

    def set_program(self):
        pass

    def set_training_to_program(self):
        pass

    def set_session(self):
        pass

    def set_user_to_session(self):
        pass

    def set_program_to_session(self):
        pass

    def set_training_to_session(self):
        pass

    def set_exercise_to_session(self):
        pass

class DBSet:
    """
    This class manages all the interactions to register data
    in the database
    """
    

    # Enregistrer un profile (plutôt dans authentification -> pas sûr que ca soit là)

    # Créer une caractéristique de mouvement

    # Créer un équipement

    # Créer un mouvement (<-- Admin)
        # Créer une association entre une caractéristique et un mouvement
        # Créer un association entre un équipement et un mouvement
    
    # Créer un exercice
        # Créer une association entre un mouvement et un exercice
    
    # Créer un entraînement
        # Créer une association entre un entraînement et un exercice
    
    # Créer un programme
        # Créer une association entre un programme et un entraînement

    # Créer une session
        # Ca consiste à plusieurs choses:
        #     - Associer un entrainements d un programme à une date
        #     - Définir si les exercices de cet entrainement sont un challenge

class DBGet:
    """
    This class manages all the interactions to get data
    in the database
    """

    # Récupérer tous les users
        # Recupérer les performances d'un user !!! --> A construire dans un second temps
    
    # Récupérer toutes les sessions
        # Récupérer une session
        # Récupérer toutes les sessions réalisées par un user
        # Récupérer toutes les sessions d'un programme
        # Récupérer toutes les sessions terminées d'un user
        # Récupérer toutes les sessions terminées d'un programme pour un user donné
        # Récupérer toutes les sessions non terminées d'un user
        # Récupérer toutes les sessions non terminées d'un programme pour un user donné
        # Récupérer toutes les sessions de la journée en cours
        # Récupérer toutes les sessions de la semaine en cours
    
    # Récupérer tous les programmes
        # Récupérer un programme
        # Récupérer tous les programmes créés par un user
        # Récupérer tous les programmes créés par un user + les programmes créés par les admins
    
    # Récupérer tous les entraînements
        # Récupérer un entraînement
        # Récupérer tous les entraînements créés par un user
        # Récupérer tous les entraînements créés par un user + les programmes créés par les admins
        # Récupérer tous les entraînements associés à un programme

    # Récupérer tous les exercices
        # Récupérer un exercice
        # Récupérer tous les exercices créés par un user
        # Récupérer tous les exercices créés par un user + les exercices créés par les admins
        # Récupérer tous les exercices associés à un programme
        # Récupérer tous les exercices associés à un entraînement

    # Récupérer tous les mouvements
        # Récupérer un mouvement
        # Récupérer tous les mouvements associés à un exercice

    # Récupérer toutes les caractéristiques de mouvement
        # Récupérer une caractéristique
        # Récupérer toutes les caractéristique d'un mouvement
        # Récupérer une caractéristique d'un mouvement

    # Récupérer tous les équipements
        # Récupérer un équipement
        # Récupérer l'équipement d'un mouvement
        # Récupérer tous les équipements d'un exercice
        # Récupérer tous les équipements d'un entraînement
        # Récupérer tous les équipements d'un programme

    pass

class DBAlter:
    """
    This class manages the interactions to modify data
    in the database
    """

    # Modifier un user
        # Modifier un mot de passe
    
    # Modifier un programme
        # Modifier le nom d'un programme
        # Modifier la date de départ d'un programme
        # Modifier la date de fin / durée d'un programme
        # Modifier la description d'un programme

    # Modifier un entraînement
        # Modifier le nom d'un entraînement

    # Modifier un exercice
        # Modifier le nom d'un exercice
        # MODIFIER L'ORDRE DES MOUVEMENTS D'UN EXERCICE

    # Modifier une session
        # Modifier la date d'une session
        # Modifier le statut done d'une session
        # Modifier/ Enregistrer la performance sur un exercice d'une session
        # Modifier le statut challenge d'un exercice d'une session

    # Modifier un équipement
        # Modifier l'équipement associé à un mouvement

    pass

class DBDelete:
    """
    This class manages the interactions to delete data
    in the database
    """

    # Supprimer un user
    # Supprimer un programme
    # Supprimer un entraînements
    # Supprimer un entraînement d'un programme
    # Supprimer un exercice
    # Supprimer un exercice d'un entraînement
    # Supprimer un mouvement
    # Supprimer un mouvement d'un exercice
    # Supprimer une caracteristique de mouvement
    # Supprimer une caracteristique de mouvement d'un mouvement
    # Supprimer une session
    # Supprimer un équipement

    pass
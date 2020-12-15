#! /usr/bin/env python3
# coding: utf-8
import math
from .tools import Tools
from .db_interactions import DBMovement, DBExercise, DBTraining
from ..models import Training, Exercise

class DataTreatment:
    """
    This class manages all the treatments to transform:
        -> DB queries in dictionnary
        -> dictionnary in DB queries
    To reach its goals, the call use all the classes from db_interactions
    """

    def __init__(self):
        self.db_mvt = DBMovement()
        self.db_exercise = DBExercise()
        self.db_training = DBTraining()
        self.tools = Tools()

    def get_all_movements_in_dict(self):
        """
        This method transforms the query set with all movement into a list of dictionnaries:
        [
            {   
                "id": movement.pk,
                "name": movement.name,
                "equipement": movement.equipment.name,
                "settings": [movement.settings.name]
            }
        ]
        """
        mvts_list = []
        mvts_queryset = self.db_mvt.get_all_movements()
        
        for mvt in mvts_queryset:
            mvt_dict = {
                "id": mvt.pk,
                "name": mvt.name,
                "equipement": mvt.equipment.name,
                "settings": [setting.name for setting in mvt.settings.all()]
            }
            mvts_list.append(mvt_dict)
        
        return mvts_list

    def register_exercise_from_dict(self, exercise_dict, user):
        """
        This method registers an exercise and all its links with movements in database
        from a dictionnary -> Received from Front so camelCase is used:
        {
            "name": "exercise_name",
            "exerciseType": "exercise_type",
            "description": "description",
            "goalType", "goal_type",
            "goalValue", "goal_value",
            "movements" : [
                {
                    "id": "movement_id",
                    "name" : "movement_name",
                    "order": "movement_order",
                    "settings": [
                        {
                            "name": "setting_name",
                            "value": "setting_value,
                        },
                        ...
                    ]
                },
                ...
            ]
        }
        """
        goal_value_converted = self._manage_goal_value_to_register(exercise_dict["goalType"], exercise_dict["goalValue"])
        exercise = self.db_exercise.set_exercise(exercise_dict["name"],
                                                exercise_dict["exerciseType"],
                                                exercise_dict["description"],
                                                exercise_dict["goalType"],
                                                goal_value_converted,
                                                user)
        if exercise:
            for movement_dict in exercise_dict["movements"]:
                movement = self.db_mvt.get_one_movement(movement_dict["name"])
                movement_associated = self.db_exercise.set_movement_to_exercise(exercise, 
                                                          movement,
                                                          movement_dict["order"])
                for setting_dict in movement_dict["settings"]:
                    setting = self.db_mvt.get_one_movement_setting(setting_dict["name"])
                    setting_associated = self.db_exercise.set_settings_value_to_movement_linked_to_exercise(movement_associated,
                                                                                                            setting,
                                                                                                            setting_dict["value"])

        return exercise

    def _manage_goal_value_to_register(self, goal_type, goal_value):
        """
        This private method ensure securiy and logic before registering numerical
        value in performance_value field in Exercise model.
        To be sure to integrate the good integer in db
        """
        
        if goal_type == "Distance" and goal_value < 100:
            goal_value = self.tools.convert_km_into_meters(goal_value)

        return goal_value

    def get_all_exercises_dict_linked_to_one_user(self, user):
        """
        This method returns all the information of the exercises associated with a user.
        in a list of dict:
            [
                {
                    "id": "exercise primary_key",
                    "name": "exercise.name",
                    "exercise_type": "exercise_type",
                    "description": "description",
                    "goal_type": "goal_type",
                    "goal_value": "goal_value",
                    "is_default": False,
                    "done": "False or True",
                    "pb: "best performance_value",
                    "movements" : [
                        {
                            "name" : "movement_name",
                            "order": "movement_order",
                            "settings": [
                                {
                                    "name": "setting_name",
                                    "value": "setting_value,
                                },
                                ...
                            ]
                        },
                        ...
                    ]
                }
            ]
        """       
        exercises = self.db_exercise.get_all_user_exercises(user)
        exercise_list = []
        for exercise in exercises:
            exercise_dict = self.get_one_exercise_in_dict_linked_to_one_user(exercise.pk, user)
            if exercise_dict:
                exercise_list.append(exercise_dict)
        return exercise_list

    def get_one_exercise_in_dict_linked_to_one_user(self, exercise_pk, user):
        """
        This method returns all the information linked to an exercise in a dictionnary.
        The method uses the primary key to get the targeted exercise
            {
                "id": "exercise primary_key",
                "name": "exercise.name",
                "exercise_type": "exercise_type",
                "description": "description",
                "goal_type": "goal_type",
                "goal_value": "goal_value",
                "is_default": False,
                "done": "False or True",
                "pb: "best performance_value",
                "movements" : [
                    {
                        "name" : "movement_name",
                        "order": "movement_order",
                        "settings": [
                            {
                                "name": "setting_name",
                                "value": "setting_value,
                            },
                            ...
                        ]
                    },
                    ...
                ]
            }
        """

        completed = True
        exercise = self.db_exercise.get_one_exercise_by_pk(exercise_pk)
        exercise_dict = {
            "id": "",
            "name": "",
            "exercise_type": "",
            "description": "",
            "goal_type": "",
            "goal_value": 0,
            "is_default": False,
            "pb": 0,
            "movements": []
        }

        # We push all informations from exercise except movements
        try:
            exercise_dict["id"] = exercise.pk
            exercise_dict["name"] = exercise.name
            exercise_dict["exercise_type"] = exercise.exercise_type
            exercise_dict["goal_type"] = exercise.goal_type
            exercise_dict["goal_value"] = exercise.goal_value
            exercise_dict["is_default"] = exercise.is_default
            exercise_dict["pb"] = self._define_pb_for_one_exercise(exercise, user)
            exercise_dict["movements"] = self._get_movements_dict_linked_to_exercise(exercise)
        except Exception as e:
            completed = False
            print("type error: " + str(e))

        try:
            exercise_dict["description"] = exercise.description
        except:
            exercise_dict["description"] = ""

        if completed:
            return exercise_dict
        else:
            return None

    def _get_pb_for_one_exercise(self, exercise, user):

        pb = self._define_pb_for_one_exercise(exercise, user)
        if exercise.goal_type == Exercise.ROUND or exercise.goal_type == Exercise.DISTANCE:
            pb = self.tools.convert_seconds_into_time_string(pb)
        return pb

    def _define_pb_for_one_exercise(self, exercise, user):
        """
        This private method return a personal record if the user register a training with this exercise
        """
        trainings = self.db_training.get_all_trainings_from_one_user_from_one_exercise(exercise, user)
        pb = 0
        if trainings and exercise.goal_type == Exercise.TIME:  
            for training in trainings:
                if training.performance_value and training.performance_value > pb:
                    pb = training.performance_value

        elif trainings and (exercise.goal_type == Exercise.ROUND or exercise.goal_type == Exercise.DISTANCE):
            for training in trainings:
                if training.performance_value and pb == 0:
                    pb = training.performance_value
                elif training.performance_value and training.performance_value < pb:
                    pb = training.performance_value
                else:
                    pass
        else:
            pass
        return pb

    def _get_movements_dict_linked_to_exercise(self,exercise):
        """
        This private method gets all the movements linked to an exercise,
        transforms them into dict and push them in a list
        """
        
        completed = True
        movements_list = []
        # We Get all movements linked to the exercise
        movements_linked = self.db_exercise.get_all_movements_linked_to_exercise(exercise)
        for movement_linked in movements_linked:
            movement_dict = {
                "id": "",
                "name": "",
                "order": "",
                "settings": [],
            }

            try:
                movement_dict["id"] = movement_linked.movement.pk
                movement_dict["name"] = movement_linked.movement.name
                movement_dict["order"] = movement_linked.movement_number
            except Exception as e:
                completed = False
                print("type error: " + str(e))
                        
            # We get all settings linked to a movement
            settings_linked = self.db_exercise.get_all_settings_linked_to_movement_linked_to_exercise(movement_linked)
            for setting_linked in settings_linked:
                setting_dict = {
                    "name": "",
                    "value": "",
                }

                try:
                    setting_dict["name"] = setting_linked.setting.name
                    setting_dict["value"] = setting_linked.setting_value
                except Exception as e:
                    completed = False
                    print("type error: " + str(e))

                movement_dict["settings"].append(setting_dict)                
            movements_list.append(movement_dict)
            
        if completed:
            return movements_list
        else:
            return None

    def get_one_training_in_dict(self, training_pk, user):
        """
        This method returns all the information linked to a training in a dictionnary.
        The method uses the primary key to get the targeted training:
            {
                "id": "training primary_key",
                "date": "training date",
                "done": "training boolean",
                "performance_type": "training perf_type",
                "performance_value": "training perf_value",
                "exercise": {
                    "id": "exercise primary_key",
                    "name": "exercise.name",
                    "exercise_type": "exercise_type",
                    "description": "description",
                    "goal_type": "goal_type",
                    "goal_value": "goal_value",
                    "is_default": False,
                    "pb": "personal best record",
                    "movements" : [
                        {
                            "name" : "movement_name",
                            "order": "movement_order",
                            "settings": [
                                {
                                    "name": "setting_name",
                                    "value": "setting_value,
                                },
                                ...
                            ]
                        },
                        ...
                    ]
                }
            }
        """
        completed = True
        training = self.db_training.get_one_training_from_pk(training_pk)
        training_dict = {
            "id": "",
            "date": "",
            "done": "",
            "performance_type": "",
            "performance_value": "",
            "exercise": {},
        }

        try:
            training_dict["id"] = training.pk
            training_dict["date"] = training.date
            training_dict["done"] = training.done
            training_dict["performance_type"] = training.performance_type
            training_dict["performance_value"] = training.performance_value
            training_dict["exercise"] = self.get_one_exercise_in_dict_linked_to_one_user(training.exercise.pk, user)
        except Exception as e:
            completed = False
            print("type error: " + str(e))
        
        if completed:
            return training_dict
        else:
            return None

    def _manage_performance_value_to_get(self, performance_type, performance_value):

        if performance_type == Training.TIME:
            performance_value = self.tools.convert_seconds_into_time_string(performance_value)

        return performance_value     

    def get_all_trainings_per_user_in_dict(self, user):    
        """
        This method returns all the trainings realized from a user in a list
        of dict order by date (from the most recent to the oldest):
            [
                {
                    "id": "training primary_key",
                    "date": "training date",
                    "done": "training boolean",
                    "performance_type": "training perf_type",
                    "performance_value": "training perf_value",
                    "exercise": {
                        "id": "exercise primary_key",
                        "name": "exercise.name",
                        "exerciseType": "exercise_type",
                        "description": "description",
                        "goal_type": "goal_type",
                        "goal_value": "goal_value",
                        "is_default": False,
                        "pb": "pb",
                        "movements" : [
                            {
                                "name" : "movement_name",
                                "order": "movement_order",
                                "settings": [
                                    {
                                        "name": "setting_name",
                                        "value": "setting_value,
                                    },
                                    ...
                                ]
                            },
                            ...
                        ]
                    }
                },
                ...
            ]
        """
        training_list= []
        trainings = self.db_training.get_all_trainings_from_one_user(user)
        for training in trainings:
            training_dict = self.get_one_training_in_dict(training.pk, user)
            if training_dict:
                training_list.append(training_dict)

        return training_list

    def get_all_trainings_per_user_linked_to_an_exercise(self, exercise, user):
        """
        This method returns all the trainings realized from a user in a list
        of dict ordered by date (from the most recent to the oldest):
            [
                {
                    "id": "training primary_key",
                    "date": "training date",
                    "done": "training boolean",
                    "performance_type": "training perf_type",
                    "performance_value": "training perf_value",
                    "exercise": {
                        "id": "exercise primary_key",
                        "name": "exercise.name",
                        "exercise_type": "exercise_type",
                        "description": "description",
                        "goal_type": "goal_type",
                        "goal_value": "goal_value",
                        "is_default": False,
                        "pb": "personal best record",
                        "movements" : [
                            {
                                "name" : "movement_name",
                                "order": "movement_order",
                                "settings": [
                                    {
                                        "name": "setting_name",
                                        "value": "setting_value,
                                    },
                                    ...
                                ]
                            },
                            ...
                        ]
                    }
                },
                ...
            ]
        """
        training_list= []
        trainings = self.db_training.get_all_trainings_from_one_user_from_one_exercise(exercise, user)
        for training in trainings:
            training_dict = self.get_one_training_in_dict(training.pk, user)
            if training_dict:
                training_list.append(training_dict)

        return training_list
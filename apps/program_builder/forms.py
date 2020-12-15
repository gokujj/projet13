from django import forms
from django.contrib.auth.forms import PasswordChangeForm
from .models import Movement, Exercise, Training


class RegisterExerciseStep1(forms.ModelForm):
    class Meta:
        model = Exercise
        fields = ['name', 'exercise_type', 'description']
        widgets = {
            'name': forms.TextInput(
                attrs={'class': 'form-control', 'required': True}
            ),
            'exercise_type': forms.Select(
                attrs={'class': 'form-control', 'required': True}
            ),
            'description': forms.Textarea(
                attrs={'class': 'form-control', 'rows': 3}
            ),
        }


class AddNewExercise(forms.ModelForm):
    class Meta:
        model = Training
        fields = [
            'exercise',
        ]
        widgets = {
            'exercise': forms.Select(
                attrs={'class': 'form-control', 'required': True}
            ),
        }


class PasswordChangeCustomForm(PasswordChangeForm):
    def __init__(self, user, *args, **kwargs):
        super().__init__(user, *args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'
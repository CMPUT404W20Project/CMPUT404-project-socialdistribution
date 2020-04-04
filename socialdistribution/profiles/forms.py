from django import forms
from django.forms import TextInput, EmailInput
from django.contrib.auth.forms import UserCreationForm
from .models import Author, User


class ProfileForm(forms.ModelForm):

    class Meta:
        model = Author
        fields = [
            'firstName',
            'lastName',
            'displayName',
            'bio',
            'github',
            'profile_img',
        ]



class UserSignup(UserCreationForm):
    password1 = forms.CharField(label=False,
                                widget=forms.TextInput(
                                    attrs={
                                        'class': 'form-control custom',
                                        'type': 'password', 'placeholder':
                                        'Password'
                                        }
                                    ),
                                )
    password2 = forms.CharField(label=False,
                                widget=forms.TextInput(
                                    attrs={
                                        'class': 'form-control custom',
                                        'type': 'password', 'placeholder':
                                        'Confirm Password'
                                        }
                                    ),
                                )

    class Meta:
        model = User
        fields = ['email', 'password1', 'password2']
        widgets = {

                    'email': EmailInput(
                                    attrs={
                                        'class': 'form-control custom',
                                        'placeholder': 'Gmail'
                                        }
                                    ),
        }

        labels = {
                    'email': False,
        }

class AuthorSignup(UserCreationForm):

    class Meta:
        model = Author
        fields = ['firstName', 'lastName']
        widgets = {
                    'firstName': TextInput(
                                    attrs={
                                        'class': 'form-control custom',
                                        'placeholder': 'First Name',
                                        }
                                    ),
                    'lastName': TextInput(
                                    attrs={
                                        'class': 'form-control custom',
                                        'placeholder': 'Last Name'
                                        }
                                    ),

        }

        labels = {
                    'firstName': False,
                    'lastName': False,
        }
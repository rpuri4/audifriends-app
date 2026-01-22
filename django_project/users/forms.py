from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Profile
from django import forms
import requests


class UserRegisterForm(UserCreationForm):
    # This class inherited from the UserCreationForm
    email = forms.EmailField()

    class Meta:
        """
        - Give listed name space for configuaration
        - Keep configuration in one space
        """
        model = User
        fields = ['username', 'email', 'password1', 'password2']


class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email']


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['image']


class FindAudioBook(forms.Form):
    audio_title = forms.CharField(max_length=500)
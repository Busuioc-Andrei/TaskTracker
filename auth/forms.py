from django import forms
from django.contrib.auth.forms import UserCreationForm

from auth.models import User


class NewUserForm(UserCreationForm):
    # email = forms.EmailField(required=True)
    email = forms.EmailField(required=False)

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

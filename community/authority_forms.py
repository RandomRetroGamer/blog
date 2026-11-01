"""
This is the start of the login methods we are going to 
do for these websites. I know Django has a built-in
secuirty options for creating and signing into accounts

We are going to import from libaries that handles these 
types of functions, and instead of storing and 
checking the passwords manually django will use 
its built in functionst to automate these things. 

File created by Randy Coronado

"""

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class SignupForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model= User
        fields = ["username", "email", "password1", "password2"]


"""
As you can wee we created a class to set up for future functions later on 
in the project, we have emails that is a requiremetn and imbedded class
that sets up model that equals to user

a field that contains a list of variables we are going to user later

"""
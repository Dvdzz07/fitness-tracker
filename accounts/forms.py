# accounts/forms.py
from django import forms
from .models import Profile


class RoleSelectionForm(forms.Form):
    """
    Form for selecting user role
    Simple form demonstrating user choice between roles
    """

    ROLE_CHOICES = [
        ("user", "User - Track workouts and join sessions"),
        ("trainer", "Trainer - All user features plus accept bookings and view client data"),
    ]

    role = forms.ChoiceField(
        choices=ROLE_CHOICES,
        widget=forms.RadioSelect,
        label="Select your role",
        initial="user"
    )

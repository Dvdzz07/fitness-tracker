from django.db import models
from django.contrib.auth.models import User


class AccountCredential(models.Model):
    """
    Stores custom password hash and salt for each user
    Linked 1-to-1 with User model
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    salt = models.CharField(max_length=32)
    password_hash = models.CharField(max_length=128)

    def __str__(self):
        return f"Credentials for {self.user.username}"


class Profile(models.Model):
    """
    User profile containing role and additional information
    Linked 1-to-1 with User model
    """

    ROLE_CHOICES = [
        ("user", "User"),
        ("trainer", "Trainer"),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="user")
    bio = models.TextField(blank=True, null=True)
    location = models.CharField(max_length=100, blank=True, null=True)
    fitness_level = models.CharField(max_length=50, blank=True, null=True)
    profile_picture = models.ImageField(upload_to="profile_pics/", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s Profile ({self.role})"

    def get_role_object(self):
        """
        Returns appropriate Role object using factory pattern
        Demonstrates OOP composition
        """
        from .roles import RoleFactory
        return RoleFactory.create_role(self.role, self.user)

    def change_role(self, new_role):
        """Updates user's role"""
        if new_role in ["user", "trainer"]:
            self.role = new_role
            self.save()
            return True
        return False

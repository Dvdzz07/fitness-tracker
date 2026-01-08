from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate

from .models import AccountCredential, Profile
from .utils.salt import NEASaltGenerator
from .utils.hashing import NEAHasher
from .forms import RoleSelectionForm


def hello(request):
    return render(request, "accounts/hello.html")


def login_view(request):
    """
    Login page for existing users
    """
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)

        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")

            user = authenticate(username=username, password=password)

            if user is not None:
                login(request, user)
                messages.success(request, f"Welcome back, {username}!")
                return redirect("accounts:dashboard")
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()

    return render(request, "accounts/login.html", {"form": form})


def logout_view(request):
    """
    Logout current user
    Handles both GET and POST requests
    """
    if request.method == "POST":
        logout(request)
        messages.success(request, "You have been logged out successfully.")
        return redirect("accounts:accounts-home")
    else:
        # GET request - show confirmation page
        logout(request)
        messages.success(request, "You have been logged out successfully.")
        return redirect("accounts:accounts-home")


def register(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)

        if form.is_valid():
            # Save the Django user
            user = form.save()

            # Get cleaned form data
            username = form.cleaned_data.get("username")
            raw_password = form.cleaned_data.get("password1")

            # Generate a per-user salt
            salt = NEASaltGenerator(username).generate()

            # Hash the password using custom hasher
            password_hash = NEAHasher(salt).hash_password(raw_password)

            # Store custom credentials
            AccountCredential.objects.create(
                user=user,
                salt=salt,
                password_hash=password_hash
            )

            # Log the new user in automatically
            login(request, user)

            messages.success(request, f"Account created for {username}!")
            return redirect("accounts:select-role")

    else:
        form = UserCreationForm()

    return render(request, "accounts/register.html", {"form": form})


@login_required
def select_role(request):
    """
    Allows user to select or change their role
    Creates Profile if it doesn't exist
    """

    # Get or create profile for user
    profile, created = Profile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        form = RoleSelectionForm(request.POST)

        if form.is_valid():
            selected_role = form.cleaned_data.get("role")

            # Update profile with selected role
            profile.role = selected_role
            profile.save()

            messages.success(request, f"Role set to {selected_role.title()}!")
            return redirect("accounts:dashboard")

    else:
        # Pre-fill form with current role
        form = RoleSelectionForm(initial={"role": profile.role})

    return render(request, "accounts/select_role.html", {"form": form, "profile": profile})


@login_required
def dashboard(request):
    """
    User dashboard - displays role-specific information
    Demonstrates polymorphism through role objects
    """

    # Get or create profile for user (handles old users without profiles)
    profile, created = Profile.objects.get_or_create(user=request.user)

    # If profile was just created, redirect to role selection
    if created:
        messages.info(request, "Please select your role to continue.")
        return redirect("accounts:select-role")

    # Get role object using factory pattern
    role_object = profile.get_role_object()

    # Get role-specific dashboard data (polymorphic call)
    dashboard_data = role_object.get_dashboard_info()

    # Get all permissions
    permissions = role_object.get_permissions()

    context = {
        "profile": profile,
        "dashboard_data": dashboard_data,
        "permissions": permissions,
        "role_object": role_object
    }

    return render(request, "accounts/dashboard.html", context)

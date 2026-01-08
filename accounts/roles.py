# accounts/roles.py
# Complex OOP Role System for NEA
# Demonstrates: inheritance, polymorphism, composition, dynamic object creation


class Role:
    """
    Base abstract role class
    Defines interface that all roles must implement
    """

    def __init__(self, user):
        self.user = user
        self.role_name = "Base Role"
        self.permissions = []

    def get_role_name(self):
        """Returns the name of the role"""
        return self.role_name

    def can_create_workout(self):
        """Check if role can create workouts"""
        raise NotImplementedError("Subclass must implement this method")

    def can_join_session(self):
        """Check if role can join group sessions"""
        raise NotImplementedError("Subclass must implement this method")

    def can_create_session(self):
        """Check if role can create group sessions"""
        raise NotImplementedError("Subclass must implement this method")

    def can_accept_bookings(self):
        """Check if role can accept trainer bookings"""
        raise NotImplementedError("Subclass must implement this method")

    def can_view_client_data(self):
        """Check if role can view client workout data"""
        raise NotImplementedError("Subclass must implement this method")

    def get_permissions(self):
        """Returns list of all permissions for this role"""
        return self.permissions

    def get_dashboard_info(self):
        """Returns role-specific dashboard information"""
        raise NotImplementedError("Subclass must implement this method")


class UserRole(Role):
    """
    Regular user role
    Inherits from Role base class
    Can do standard user activities
    """

    def __init__(self, user):
        super().__init__(user)
        self.role_name = "User"
        self.permissions = [
            "create_workout",
            "join_session",
            "create_session",
            "view_own_data"
        ]

    def can_create_workout(self):
        """Users can create their own workouts"""
        return True

    def can_join_session(self):
        """Users can join group fitness sessions"""
        return True

    def can_create_session(self):
        """Users can create group sessions"""
        return True

    def can_accept_bookings(self):
        """Regular users cannot accept trainer bookings"""
        return False

    def can_view_client_data(self):
        """Regular users cannot view other users' data"""
        return False

    def get_dashboard_info(self):
        """Returns user-specific dashboard data"""
        data = {
            "role": self.role_name,
            "username": self.user.username,
            "features": [
                "Track workouts",
                "Join group sessions",
                "Create sessions",
                "View exercise library"
            ],
            "message": f"Welcome back, {self.user.username}!"
        }
        return data


class TrainerRole(Role):
    """
    Trainer role - extends user capabilities
    Inherits from Role base class
    Has additional permissions plus all user permissions
    """

    def __init__(self, user):
        super().__init__(user)
        self.role_name = "Trainer"
        self.permissions = [
            "create_workout",
            "join_session",
            "create_session",
            "view_own_data",
            "accept_bookings",
            "view_client_data",
            "create_workout_plans"
        ]
        self.specialities = []

    def can_create_workout(self):
        """Trainers can create workouts (same as users)"""
        return True

    def can_join_session(self):
        """Trainers can join sessions (same as users)"""
        return True

    def can_create_session(self):
        """Trainers can create sessions (same as users)"""
        return True

    def can_accept_bookings(self):
        """Trainers can accept client bookings (unique to trainers)"""
        return True

    def can_view_client_data(self):
        """Trainers can view their clients' workout data (unique to trainers)"""
        return True

    def set_specialities(self, speciality_list):
        """Set trainer's areas of expertise"""
        self.specialities = speciality_list

    def get_specialities(self):
        """Get trainer's specialities"""
        return self.specialities

    def get_dashboard_info(self):
        """Returns trainer-specific dashboard data"""
        data = {
            "role": self.role_name,
            "username": self.user.username,
            "features": [
                "Track workouts",
                "Join group sessions",
                "Create sessions",
                "Accept client bookings",
                "View client progress",
                "Create workout plans"
            ],
            "message": f"Welcome back, Trainer {self.user.username}!",
            "specialities": self.specialities
        }
        return data


class RoleFactory:
    """
    Factory pattern for dynamic role creation
    Creates appropriate role object based on role type
    Demonstrates composition and dynamic object instantiation
    """

    # Class-level dictionary mapping role names to classes
    ROLE_CLASSES = {
        "user": UserRole,
        "trainer": TrainerRole
    }

    @staticmethod
    def create_role(role_type, user):
        """
        Factory method - creates and returns appropriate role object

        Args:
            role_type: string ("user" or "trainer")
            user: Django User object

        Returns:
            Role object (UserRole or TrainerRole instance)
        """
        role_type_lower = role_type.lower()

        # Check if role type exists in our mapping
        if role_type_lower in RoleFactory.ROLE_CLASSES:
            role_class = RoleFactory.ROLE_CLASSES[role_type_lower]
            return role_class(user)
        else:
            # Default to UserRole if unknown type
            return UserRole(user)

    @staticmethod
    def get_available_roles():
        """Returns list of all available role types"""
        return list(RoleFactory.ROLE_CLASSES.keys())


class RoleManager:
    """
    Manages role operations for a user
    Composition - contains a Role object
    Provides interface for checking permissions
    """

    def __init__(self, user, role_type):
        self.user = user
        self.role = RoleFactory.create_role(role_type, user)

    def get_role(self):
        """Returns the current role object"""
        return self.role

    def change_role(self, new_role_type):
        """Changes user's role to a new type"""
        self.role = RoleFactory.create_role(new_role_type, self.user)

    def check_permission(self, permission_name):
        """
        Check if user has a specific permission
        Uses polymorphism - calls appropriate method based on role type
        """
        if permission_name == "create_workout":
            return self.role.can_create_workout()
        elif permission_name == "join_session":
            return self.role.can_join_session()
        elif permission_name == "create_session":
            return self.role.can_create_session()
        elif permission_name == "accept_bookings":
            return self.role.can_accept_bookings()
        elif permission_name == "view_client_data":
            return self.role.can_view_client_data()
        else:
            return False

    def get_all_permissions(self):
        """Returns all permissions for current role"""
        return self.role.get_permissions()

    def get_dashboard_info(self):
        """Gets dashboard data - polymorphic call"""
        return self.role.get_dashboard_data()

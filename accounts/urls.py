from django.urls import path
from . import views

app_name = "accounts"

urlpatterns = [
    path("", views.hello, name="accounts-home"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("register/", views.register, name="register"),
    path("select-role/", views.select_role, name="select-role"),
    path("dashboard/", views.dashboard, name="dashboard"),
]


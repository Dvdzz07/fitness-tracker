from django.urls import path
from . import views

app_name = 'fitness_sessions'

urlpatterns = [
    path('', views.session_list, name='session-list'),
    path('create/', views.create_session, name='create-session'),
    path('<int:session_id>/', views.session_detail, name='session-detail'),
    path('<int:session_id>/join/', views.join_session, name='join-session'),
    path('<int:session_id>/leave/', views.leave_session, name='leave-session'),
    path('api/sessions/', views.get_sessions_json, name='sessions-json'),
]

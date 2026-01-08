from django.urls import path
from . import views

app_name = 'trainer_bookings'

urlpatterns = [
    path('', views.booking_list, name='booking-list'),
    path('create/', views.create_booking, name='create-booking'),
    path('<int:booking_id>/', views.booking_detail, name='booking-detail'),
    path('<int:booking_id>/cancel/', views.cancel_booking, name='cancel-booking'),
    path('trainer/<int:trainer_id>/process/', views.process_trainer_bookings, name='process-bookings'),
    path('trainer/<int:trainer_id>/queue/', views.view_priority_queue, name='view-queue'),
]

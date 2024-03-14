from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.subscriber_login, name='subscriber-login'),
    # Ensure you have paths for 'manage-subscription' and 'login-error' views as well
    path('manage-subscription/', views.manage_subscription, name='manage-subscription'),
    path('logout/', views.subscriber_logout, name='subscriber-logout'),
    path('events/download/<uuid:ref_token>/', views.download_ics_file, name='download_ics_event'),
]


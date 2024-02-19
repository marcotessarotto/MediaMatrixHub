from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.subscriber_login, name='subscriber_login'),
    # Ensure you have paths for 'manage-subscription' and 'login-error' views as well
    path('manage-subscription/', views.manage_subscription, name='manage-subscription'),
]

from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/seeker/edit/', views.edit_seeker_profile, name='edit_seeker_profile'),
    path('profile/employer/edit/', views.edit_employer_profile, name='edit_employer_profile'),
]

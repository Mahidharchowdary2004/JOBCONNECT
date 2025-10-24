from django.urls import path
from . import views

app_name = 'jobs'

urlpatterns = [
    path('', views.home, name='home'),
    path('jobs/', views.job_list, name='job_list'),
    path('job/<int:job_id>/', views.job_detail, name='job_detail'),
    path('job/create/', views.create_job, name='create_job'),
    path('job/<int:job_id>/edit/', views.edit_job, name='edit_job'),
    path('job/<int:job_id>/delete/', views.delete_job, name='delete_job'),
    path('job/<int:job_id>/apply/', views.apply_job, name='apply_job'),
    path('job/<int:job_id>/applicants/', views.view_applicants, name='view_applicants'),
    path('application/<int:application_id>/update/', views.update_application_status, name='update_application_status'),
    path('application/<int:application_id>/delete/', views.delete_application, name='delete_application'),
]
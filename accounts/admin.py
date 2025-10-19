from django.contrib import admin
from .models import UserProfile, JobSeekerProfile, EmployerProfile

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'role', 'phone', 'created_at']
    list_filter = ['role', 'created_at']
    search_fields = ['user__username', 'user__email', 'phone']

@admin.register(JobSeekerProfile)
class JobSeekerProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'location', 'experience_years']
    search_fields = ['user__username', 'skills', 'location']
    list_filter = ['experience_years']

@admin.register(EmployerProfile)
class EmployerProfileAdmin(admin.ModelAdmin):
    list_display = ['company_name', 'user', 'industry', 'location']
    search_fields = ['company_name', 'industry', 'location']
    list_filter = ['industry']

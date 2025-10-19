from django.contrib import admin
from .models import Job, Application

@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ['title', 'employer', 'category', 'job_type', 'location', 'is_active', 'posted_date']
    list_filter = ['job_type', 'experience_level', 'is_active', 'posted_date', 'category']
    search_fields = ['title', 'description', 'category', 'location']
    date_hierarchy = 'posted_date'

@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ['applicant', 'job', 'status', 'applied_date']
    list_filter = ['status', 'applied_date']
    search_fields = ['applicant__username', 'job__title']
    date_hierarchy = 'applied_date'

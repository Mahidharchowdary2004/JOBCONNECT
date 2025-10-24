from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from django.db.models.manager import Manager

class Job(models.Model):
    if TYPE_CHECKING:
        applications: Any
        objects: Any
    
    JOB_TYPE_CHOICES = (
        ('full-time', 'Full Time'),
        ('part-time', 'Part Time'),
        ('contract', 'Contract'),
        ('internship', 'Internship'),
        ('remote', 'Remote'),
    )
    
    EXPERIENCE_LEVEL = (
        ('entry', 'Entry Level'),
        ('mid', 'Mid Level'),
        ('senior', 'Senior Level'),
        ('executive', 'Executive'),
    )
    
    employer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='job_posts')
    title = models.CharField(max_length=200)
    description = models.TextField()
    requirements = models.TextField()
    responsibilities = models.TextField(blank=True)
    job_type = models.CharField(max_length=20, choices=JOB_TYPE_CHOICES)
    experience_level = models.CharField(max_length=20, choices=EXPERIENCE_LEVEL)
    category = models.CharField(max_length=100)
    location = models.CharField(max_length=200)
    salary_min = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    salary_max = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    is_active = models.BooleanField(default=True)  # type: ignore
    posted_date = models.DateTimeField(auto_now_add=True)
    deadline = models.DateField(blank=True, null=True)
    
    class Meta:
        ordering = ['-posted_date']
    
    def __str__(self) -> str:
        return str(self.title)
    
    def applications_count(self) -> int:
        return self.applications.count()

class Application(models.Model):
    if TYPE_CHECKING:
        objects: Any
        
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('reviewing', 'Under Review'),
        ('shortlisted', 'Shortlisted'),
        ('rejected', 'Rejected'),
        ('accepted', 'Accepted'),
    )
    
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='applications')
    applicant = models.ForeignKey(User, on_delete=models.CASCADE, related_name='applications')
    cover_letter = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    applied_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)  # type: ignore
    
    class Meta:
        ordering = ['-applied_date']
        unique_together = ['job', 'applicant']
    
    def __str__(self) -> str:
        # These attributes exist at runtime but type checkers can't see them
        applicant_username = getattr(self.applicant, 'username', 'Unknown User')
        job_title = getattr(self.job, 'title', 'Unknown Job')
        return f"{applicant_username} - {job_title}"
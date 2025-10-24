from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.utils import timezone
from functools import reduce
from operator import or_
from django.core.mail import send_mail
from django.conf import settings
from .models import Job, Application

def home(request):
    recent_jobs = Job.objects.filter(is_active=True).select_related('employer__employer_profile')[:6]
    return render(request, 'jobs/home.html', {'recent_jobs': recent_jobs})

def job_list(request):
    jobs = Job.objects.filter(is_active=True).select_related('employer__employer_profile')
    
    search_query = request.GET.get('search', '')
    location = request.GET.get('location', '')
    job_type = request.GET.get('job_type', '')
    category = request.GET.get('category', '')
    experience_level = request.GET.get('experience_level', '')
    
    if search_query:
        # Create a list of Q objects and combine them using reduce
        q_objects = [
            Q(title__icontains=search_query),
            Q(description__icontains=search_query),
            Q(requirements__icontains=search_query)
        ]
        # Use reduce with or_ operator to combine all Q objects
        combined_q = reduce(or_, q_objects)
        jobs = jobs.filter(combined_q)
    
    if location:
        jobs = jobs.filter(location__icontains=location)
    
    if job_type:
        jobs = jobs.filter(job_type=job_type)
    
    if category:
        jobs = jobs.filter(category__icontains=category)
    
    if experience_level:
        jobs = jobs.filter(experience_level=experience_level)
    
    # Calculate statistics for the quick stats section
    total_jobs = Job.objects.filter(is_active=True).count()
    # For featured jobs, let's use a more appropriate filter
    featured_jobs = Job.objects.filter(is_active=True).count()  # All active jobs for now
    remote_jobs = Job.objects.filter(is_active=True, job_type='remote').count()
    # For new today, we need to filter on the base queryset, not the filtered one
    new_today = Job.objects.filter(is_active=True, posted_date__date=timezone.now().date()).count()
    
    context = {
        'jobs': jobs,
        'search_query': search_query,
        'location': location,
        'job_type': job_type,
        'category': category,
        'experience_level': experience_level,
        'total_jobs': total_jobs,
        'featured_jobs': featured_jobs,
        'remote_jobs': remote_jobs,
        'new_today': new_today,
    }
    
    return render(request, 'jobs/job_list.html', context)

def job_detail(request, job_id):
    job = get_object_or_404(Job, id=job_id)
    
    has_applied = False
    if request.user.is_authenticated:
        has_applied = Application.objects.filter(job=job, applicant=request.user).exists()
    
    return render(request, 'jobs/job_detail.html', {'job': job, 'has_applied': has_applied})

@login_required
def create_job(request):
    if request.user.profile.role != 'employer':
        messages.error(request, 'Only employers can post jobs!')
        return redirect('jobs:home')
    
    if request.method == 'POST':
        job = Job.objects.create(
            employer=request.user,
            title=request.POST.get('title'),
            description=request.POST.get('description'),
            requirements=request.POST.get('requirements'),
            responsibilities=request.POST.get('responsibilities', ''),
            job_type=request.POST.get('job_type'),
            experience_level=request.POST.get('experience_level'),
            category=request.POST.get('category'),
            location=request.POST.get('location'),
            salary_min=request.POST.get('salary_min') or None,
            salary_max=request.POST.get('salary_max') or None,
            deadline=request.POST.get('deadline') or None,
        )
        messages.success(request, 'Job posted successfully!')
        return redirect('jobs:job_detail', job_id=job.id)
    
    return render(request, 'jobs/create_job.html')

@login_required
def edit_job(request, job_id):
    job = get_object_or_404(Job, id=job_id, employer=request.user)
    
    if request.method == 'POST':
        job.title = request.POST.get('title')
        job.description = request.POST.get('description')
        job.requirements = request.POST.get('requirements')
        job.responsibilities = request.POST.get('responsibilities', '')
        job.job_type = request.POST.get('job_type')
        job.experience_level = request.POST.get('experience_level')
        job.category = request.POST.get('category')
        job.location = request.POST.get('location')
        job.salary_min = request.POST.get('salary_min') or None
        job.salary_max = request.POST.get('salary_max') or None
        job.deadline = request.POST.get('deadline') or None
        job.is_active = request.POST.get('is_active') == 'on'
        job.save()
        
        messages.success(request, 'Job updated successfully!')
        return redirect('jobs:job_detail', job_id=job.id)
    
    return render(request, 'jobs/edit_job.html', {'job': job})

@login_required
def delete_job(request, job_id):
    job = get_object_or_404(Job, id=job_id, employer=request.user)
    
    if request.method == 'POST':
        # Add some debugging information
        job_title = job.title
        applications_count = job.applications.count()
        
        job.delete()
        messages.success(request, f'Job "{job_title}" and {applications_count} application(s) deleted successfully!')
        return redirect('accounts:dashboard')
    
    return render(request, 'jobs/delete_job.html', {'job': job})

@login_required
def apply_job(request, job_id):
    job = get_object_or_404(Job, id=job_id, is_active=True)
    
    if request.user.profile.role != 'seeker':
        messages.error(request, 'Only job seekers can apply for jobs!')
        return redirect('jobs:job_detail', job_id=job_id)
    
    if Application.objects.filter(job=job, applicant=request.user).exists():
        messages.warning(request, 'You have already applied for this job!')
        return redirect('jobs:job_detail', job_id=job_id)
    
    if request.method == 'POST':
        cover_letter = request.POST.get('cover_letter', '')
        Application.objects.create(
            job=job,
            applicant=request.user,
            cover_letter=cover_letter
        )
        messages.success(request, 'Application submitted successfully!')
        return redirect('accounts:dashboard')
    
    return render(request, 'jobs/apply_job.html', {'job': job})

@login_required
def view_applicants(request, job_id):
    job = get_object_or_404(Job, id=job_id, employer=request.user)
    applications = job.applications.all()
    
    # Calculate statistics for the template
    pending_count = applications.filter(status='pending').count()
    shortlisted_count = applications.filter(status='shortlisted').count()
    accepted_count = applications.filter(status='accepted').count()
    
    # Prepare JSON data for the template
    import json
    from django.core.serializers import serialize
    from django.forms.models import model_to_dict
    
    applications_data = []
    for application in applications:
        applications_data.append({
            'id': application.id,
            'name': application.applicant.get_full_name() or application.applicant.username,
            'email': application.applicant.email,
            'phone': application.applicant.profile.phone if hasattr(application.applicant, 'profile') and application.applicant.profile.phone else 'Not provided',
            'position': job.title,
            'date': application.applied_date.strftime('%Y-%m-%d'),
            'status': application.status  # This will include all status values including 'reviewing'
        })
    
    applications_json = json.dumps(applications_data)
    
    return render(request, 'jobs/view_applicants.html', {
        'job': job, 
        'applications': applications,
        'pending_count': pending_count,
        'shortlisted_count': shortlisted_count,
        'accepted_count': accepted_count,
        'applications_json': applications_json
    })

@login_required
def update_application_status(request, application_id):
    application = get_object_or_404(Application, id=application_id)
    
    if application.job.employer != request.user:
        messages.error(request, 'You do not have permission to update this application!')
        return redirect('accounts:dashboard')
    
    if request.method == 'POST':
        status = request.POST.get('status')
        # Validate that status is provided and is a valid choice
        if status and status in dict(Application.STATUS_CHOICES):
            old_status = application.status
            application.status = status
            application.save()
            
            # Send email notification when status changes
            send_application_status_email(application, old_status, status)
            
            messages.success(request, 'Application status updated successfully!')
        else:
            messages.error(request, 'Please select a valid status.')
    
    # Always redirect back to the applicants page
    return redirect('jobs:view_applicants', job_id=application.job.id)


def send_application_status_email(application, old_status, new_status):
    """Send email notification when application status is updated"""
    try:
        # Get applicant email
        applicant_email = application.applicant.email
        if not applicant_email:
            return  # No email to send to
            
        # Prepare email content
        subject = f"Application Status Update for {application.job.title}"
        
        # Create message based on status change
        if new_status == 'rejected':
            message = f"""Dear {application.applicant.username},

We regret to inform you that your application for the position "{application.job.title}" at {application.job.employer.employer_profile.company_name} has been {new_status}.

Status Details:
- Previous Status: {old_status}
- New Status: {new_status}
- Position: {application.job.title}
- Company: {application.job.employer.employer_profile.company_name}
- Applied Date: {application.applied_date.strftime('%Y-%m-%d')}

Thank you for your interest in our company.

Best regards,
{application.job.employer.employer_profile.company_name} Hiring Team
"""
        elif new_status == 'accepted':
            message = f"""Dear {application.applicant.username},

Congratulations! Your application for the position "{application.job.title}" at {application.job.employer.employer_profile.company_name} has been {new_status}.

Status Details:
- Previous Status: {old_status}
- New Status: {new_status}
- Position: {application.job.title}
- Company: {application.job.employer.employer_profile.company_name}
- Applied Date: {application.applied_date.strftime('%Y-%m-%d')}

We will contact you shortly with next steps.

Best regards,
{application.job.employer.employer_profile.company_name} Hiring Team
"""
        else:
            # Generic message for other status updates
            message = f"""Dear {application.applicant.username},

Your application status for the position "{application.job.title}" at {application.job.employer.employer_profile.company_name} has been updated.

Status Details:
- Previous Status: {old_status}
- New Status: {new_status}
- Position: {application.job.title}
- Company: {application.job.employer.employer_profile.company_name}
- Applied Date: {application.applied_date.strftime('%Y-%m-%d')}

We will notify you of any further updates.

Best regards,
{application.job.employer.employer_profile.company_name} Hiring Team
"""
        
        # Send email
        # Note: In a real application, you would configure proper email settings
        # For now, we'll use a placeholder that prints to console
        print(f"EMAIL SENT TO: {applicant_email}")
        print(f"SUBJECT: {subject}")
        print(f"MESSAGE: {message}")
        print("---")
        
        # In a production environment, you would uncomment the following line:
        # send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [applicant_email])
        
    except Exception as e:
        # Log error but don't interrupt the flow
        print(f"Failed to send email notification: {str(e)}")


@login_required
def delete_application(request, application_id):
    application = get_object_or_404(Application, id=application_id)
    
    # Check if user is either the job employer or the applicant
    is_employer = application.job.employer == request.user
    is_applicant = application.applicant == request.user
    
    if not (is_employer or is_applicant):
        messages.error(request, 'You do not have permission to delete this application!')
        return redirect('accounts:dashboard')
    
    # Determine redirect URL based on who is deleting
    if is_employer:
        redirect_url = 'jobs:view_applicants'
        job_id = application.job.id
    else:  # is_applicant
        redirect_url = 'accounts:dashboard'
        job_id = None
    
    if request.method == 'POST':
        application.delete()
        messages.success(request, 'Application deleted successfully!')
        if is_employer:
            return redirect(redirect_url, job_id=job_id)
        else:
            return redirect(redirect_url)
    
    # For GET requests, show confirmation page
    return render(request, 'jobs/delete_application.html', {
        'application': application,
        'is_employer': is_employer,
        'is_applicant': is_applicant
    })

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import Job, Application

def home(request):
    recent_jobs = Job.objects.filter(is_active=True)[:6]
    return render(request, 'jobs/home.html', {'recent_jobs': recent_jobs})

def job_list(request):
    jobs = Job.objects.filter(is_active=True)
    
    search_query = request.GET.get('search', '')
    location = request.GET.get('location', '')
    job_type = request.GET.get('job_type', '')
    category = request.GET.get('category', '')
    experience_level = request.GET.get('experience_level', '')
    
    if search_query:
        jobs = jobs.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(requirements__icontains=search_query)
        )
    
    if location:
        jobs = jobs.filter(location__icontains=location)
    
    if job_type:
        jobs = jobs.filter(job_type=job_type)
    
    if category:
        jobs = jobs.filter(category__icontains=category)
    
    if experience_level:
        jobs = jobs.filter(experience_level=experience_level)
    
    context = {
        'jobs': jobs,
        'search_query': search_query,
        'location': location,
        'job_type': job_type,
        'category': category,
        'experience_level': experience_level,
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
        job.delete()
        messages.success(request, 'Job deleted successfully!')
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
    
    return render(request, 'jobs/view_applicants.html', {'job': job, 'applications': applications})

@login_required
def update_application_status(request, application_id):
    application = get_object_or_404(Application, id=application_id)
    
    if application.job.employer != request.user:
        messages.error(request, 'You do not have permission to update this application!')
        return redirect('accounts:dashboard')
    
    if request.method == 'POST':
        status = request.POST.get('status')
        application.status = status
        application.save()
        messages.success(request, 'Application status updated successfully!')
    
    return redirect('jobs:view_applicants', job_id=application.job.id)

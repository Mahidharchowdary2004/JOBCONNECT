from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from .models import UserProfile, JobSeekerProfile, EmployerProfile

def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        role = request.POST.get('role')
        
        if password != password2:
            messages.error(request, 'Passwords do not match!')
            return render(request, 'accounts/register.html')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists!')
            return render(request, 'accounts/register.html')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists!')
            return render(request, 'accounts/register.html')
        
        user = User.objects.create_user(username=username, email=email, password=password)
        user.first_name = request.POST.get('first_name', '')
        user.last_name = request.POST.get('last_name', '')
        user.save()
        
        profile = UserProfile.objects.get(user=user)
        profile.role = role
        profile.phone = request.POST.get('phone', '')
        profile.save()
        
        if role == 'seeker':
            JobSeekerProfile.objects.create(user=user)
        elif role == 'employer':
            company_name = request.POST.get('company_name', 'Company')
            EmployerProfile.objects.create(user=user, company_name=company_name)
        
        messages.success(request, 'Account created successfully! Please login.')
        return redirect('accounts:login')
    
    return render(request, 'accounts/register.html')

def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')
            return redirect('accounts:dashboard')
        else:
            messages.error(request, 'Invalid username or password!')
    
    return render(request, 'accounts/login.html')

@login_required
def user_logout(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully!')
    return redirect('jobs:home')

@login_required
def dashboard(request):
    user_profile = request.user.profile
    
    if user_profile.role == 'seeker':
        seeker_profile = JobSeekerProfile.objects.get_or_create(user=request.user)[0]
        applications = request.user.applications.all()
        context = {
            'seeker_profile': seeker_profile,
            'applications': applications,
        }
        return render(request, 'accounts/seeker_dashboard.html', context)
    
    elif user_profile.role == 'employer':
        employer_profile = EmployerProfile.objects.get_or_create(user=request.user)[0]
        jobs = request.user.job_posts.all()
        context = {
            'employer_profile': employer_profile,
            'jobs': jobs,
        }
        return render(request, 'accounts/employer_dashboard.html', context)
    
    return render(request, 'accounts/dashboard.html')

@login_required
def edit_seeker_profile(request):
    seeker_profile = JobSeekerProfile.objects.get_or_create(user=request.user)[0]
    
    if request.method == 'POST':
        seeker_profile.skills = request.POST.get('skills', '')
        seeker_profile.experience_years = request.POST.get('experience_years', 0)
        seeker_profile.education = request.POST.get('education', '')
        seeker_profile.bio = request.POST.get('bio', '')
        seeker_profile.location = request.POST.get('location', '')
        seeker_profile.linkedin_url = request.POST.get('linkedin_url', '')
        seeker_profile.portfolio_url = request.POST.get('portfolio_url', '')
        
        if request.FILES.get('profile_picture'):
            seeker_profile.profile_picture = request.FILES['profile_picture']
        
        if request.FILES.get('resume'):
            seeker_profile.resume = request.FILES['resume']
        
        seeker_profile.save()
        
        user = request.user
        user.first_name = request.POST.get('first_name', '')
        user.last_name = request.POST.get('last_name', '')
        user.email = request.POST.get('email', '')
        user.save()
        
        messages.success(request, 'Profile updated successfully!')
        return redirect('accounts:dashboard')
    
    return render(request, 'accounts/edit_seeker_profile.html', {'seeker_profile': seeker_profile})

@login_required
def edit_employer_profile(request):
    employer_profile = EmployerProfile.objects.get_or_create(user=request.user)[0]
    
    if request.method == 'POST':
        employer_profile.company_name = request.POST.get('company_name', '')
        employer_profile.company_description = request.POST.get('company_description', '')
        employer_profile.company_website = request.POST.get('company_website', '')
        employer_profile.company_size = request.POST.get('company_size', '')
        employer_profile.industry = request.POST.get('industry', '')
        employer_profile.location = request.POST.get('location', '')
        
        if request.FILES.get('company_logo'):
            employer_profile.company_logo = request.FILES['company_logo']
        
        employer_profile.save()
        
        user = request.user
        user.first_name = request.POST.get('first_name', '')
        user.last_name = request.POST.get('last_name', '')
        user.email = request.POST.get('email', '')
        user.save()
        
        messages.success(request, 'Company profile updated successfully!')
        return redirect('accounts:dashboard')
    
    return render(request, 'accounts/edit_employer_profile.html', {'employer_profile': employer_profile})

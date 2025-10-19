# Job Portal Web Application

## Overview
A full-stack job portal web application built with Django that connects job seekers with employers. The platform features role-based authentication, profile management, job posting and application systems, and a responsive Bootstrap interface.

## Recent Changes
- **October 19, 2025**: Initial implementation of complete job portal system
  - Set up Django project with PostgreSQL database
  - Implemented user authentication with role-based access (Job Seeker/Employer)
  - Created models for user profiles, job postings, and applications
  - Built responsive UI with Bootstrap 5
  - Configured Django admin panel for all models
  - Set up media file uploads for resumes and profile pictures

## Project Architecture

### Stack
- **Backend**: Django 5.2.7 (Python web framework)
- **Database**: PostgreSQL (Neon-backed via Replit)
- **Frontend**: Bootstrap 5, jQuery, Font Awesome
- **Forms**: django-crispy-forms with Bootstrap 5

### Apps Structure
- **accounts**: User authentication, profiles (Job Seeker & Employer)
- **jobs**: Job postings, applications, and applicant management

### Key Models
- `UserProfile`: Extends User with role (seeker/employer) and phone
- `JobSeekerProfile`: Resume, skills, experience, education, portfolio
- `EmployerProfile`: Company info, logo, description, industry
- `Job`: Job postings with details, requirements, salary range
- `Application`: Job applications with status tracking

### Features Implemented
1. **Authentication System**
   - User registration with role selection (Job Seeker/Employer)
   - Login/Logout functionality
   - Role-based dashboard redirection

2. **Job Seeker Features**
   - Profile management with resume upload
   - Browse and search jobs with filters
   - Apply for jobs with cover letter
   - View application status

3. **Employer Features**
   - Company profile management
   - Create, edit, and manage job postings
   - View and manage applicants
   - Update application status

4. **Job Management**
   - Search and filter by location, job type, category, experience level
   - Job details with requirements and responsibilities
   - Active/Inactive status management

5. **Admin Panel**
   - Full CRUD operations for all models
   - User and profile management
   - Job and application oversight

## User Preferences
- None specified yet

## Environment Variables
- `DATABASE_URL`: PostgreSQL connection string
- `PGDATABASE`, `PGUSER`, `PGPASSWORD`, `PGHOST`, `PGPORT`: Database credentials
- `SESSION_SECRET`: Django secret key

## Running the Application
The Django development server runs automatically on port 5000. Access the application at the Replit webview.

### Admin Panel
Access at `/admin/` - create a superuser first:
```bash
python manage.py createsuperuser
```

### Key URLs
- Home: `/`
- Browse Jobs: `/jobs/`
- Register: `/accounts/register/`
- Login: `/accounts/login/`
- Dashboard: `/accounts/dashboard/`
- Post Job: `/job/create/` (Employers only)

## Future Enhancements
- Email notifications for applications and status updates
- Advanced search with saved searches and job alerts
- REST API with Django REST Framework
- Applicant tracking with interview scheduling
- Company reviews and ratings

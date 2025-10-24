from django.contrib.auth import logout
from django.utils import timezone
from django.conf import settings
from django.shortcuts import redirect
from django.contrib import messages
from django.utils.timezone import is_naive, make_aware

class SessionTimeoutMiddleware:
    """
    Middleware to handle session timeout for both job seekers and employers.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Skip middleware for static files and media
        if request.path.startswith('/static/') or request.path.startswith('/media/'):
            return self.get_response(request)
            
        # Check if user is authenticated
        if request.user.is_authenticated:
            # Get the last activity time from session
            last_activity = request.session.get('last_activity')
            
            if last_activity:
                try:
                    # Convert to datetime object
                    last_activity_time = timezone.datetime.fromisoformat(last_activity)
                    
                    # Make sure it's timezone aware
                    if is_naive(last_activity_time):
                        last_activity_time = make_aware(last_activity_time)
                    
                    # Check if session has expired (30 minutes = 1800 seconds)
                    if (timezone.now() - last_activity_time).seconds > settings.SESSION_COOKIE_AGE:
                        # Session has expired, log out user
                        logout(request)
                        messages.warning(request, 'Your session has expired due to inactivity. Please log in again.')
                        return redirect('accounts:login')
                except (ValueError, TypeError) as e:
                    # Handle potential issues with datetime parsing
                    pass
            
            # Update last activity time
            request.session['last_activity'] = timezone.now().isoformat()
        
        response = self.get_response(request)
        return response
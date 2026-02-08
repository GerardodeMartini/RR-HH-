from django.contrib.auth import logout
from django.shortcuts import redirect

def custom_logout(request, next_page=None):
    logout(request)
    # Check if a 'next' parameter is passed in the GET request (e.g., ?next=/some/url/)
    if not next_page:
        next_page = request.GET.get('next', '/')
    return redirect(next_page)

from functools import wraps
from django.shortcuts import redirect


def org_login_required(view_func):
    """
    Decorator that ensures the user is logged into an organization.
    Redirects to login page if no org session exists.
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.organization:
            return redirect('org_login')
        return view_func(request, *args, **kwargs)
    return wrapper

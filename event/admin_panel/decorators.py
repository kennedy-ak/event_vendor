from django.shortcuts import redirect
from django.contrib import messages


def admin_required(view_func):
    """
    Decorator to restrict view access to users with admin role only.
    Redirects to home page with error message if user is not an admin.
    """
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, 'You must be logged in to access the admin panel.')
            return redirect('login')

        if request.user.role != 'admin':
            messages.error(request, 'You do not have permission to access the admin panel.')
            return redirect('home')

        return view_func(request, *args, **kwargs)

    return wrapper

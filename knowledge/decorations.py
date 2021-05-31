from django.shortcuts import redirect, render
from django.http import HttpResponse

# function to define which roles are allowed to perform a specific task, for example only a Garderner can create a Seed
def allowed_users(allowed_roles=[]):
    def decorator(view_function):
        def wrapper_func(request, *args, **kwargs):
            group = None
            if request.user.groups.exists():
                group = request.user.groups.all()[0].name
            if group in allowed_roles:
                return view_function(request, *args, **kwargs)
            else:
                return render(request, "dist/inside/seed/404_not_allowed.html")
        return wrapper_func
    return decorator


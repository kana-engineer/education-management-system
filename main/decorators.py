from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages


def admin_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated or getattr(request.user, 'role', None) != 'admin':
            messages.error(request, 'Доступ запрещён!')
            from django.urls import reverse
            login_url = reverse('main:login')
            next_url = request.get_full_path()
            return redirect(f'{login_url}?next={next_url}')
        return view_func(request, *args, **kwargs)
    return _wrapped_view

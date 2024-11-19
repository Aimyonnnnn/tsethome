from functools import wraps
from flask import session, redirect

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin' not in session:
            return redirect('/admin/login')
        return f(*args, **kwargs)
    return decorated_function
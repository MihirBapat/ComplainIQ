"""Staff authentication and role authorization."""
from functools import wraps
from flask import Blueprint, flash, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash
from app.db import query_one

bp = Blueprint("auth", __name__)

def role_required(*roles):
    """Require a signed-in staff member in one of the allowed roles."""
    def decorator(view):
        @wraps(view)
        def wrapped(*args, **kwargs):
            if session.get("role") not in roles:
                flash("Please sign in with an authorized staff account.", "warning")
                return redirect(url_for("auth.login"))
            return view(*args, **kwargs)
        return wrapped
    return decorator

@bp.route("/login", methods=("GET", "POST"))
def login():
    if request.method == "POST":
        staff = query_one("SELECT * FROM staff WHERE username=?", (request.form.get("username", "").strip(),))
        if staff and check_password_hash(staff["password_hash"], request.form.get("password", "")):
            session.clear(); session.update(staff_id=staff["staff_id"], username=staff["username"], role=staff["role"])
            return redirect(url_for("index"))
        flash("Invalid username or password.", "danger")
    return render_template("auth/login.html")

@bp.get("/logout")
def logout():
    session.clear(); flash("You have been signed out.", "info")
    return redirect(url_for("auth.login"))

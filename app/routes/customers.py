"""Customer CRUD routes."""
from flask import Blueprint, flash, redirect, render_template, request, url_for
from app.auth import role_required
from app.db import execute, query_all, query_one
bp = Blueprint("customers", __name__, url_prefix="/customers")

@bp.route("", methods=("GET", "POST"))
@role_required("ADMIN")
def index():
    if request.method == "POST":
        try:
            execute("INSERT INTO customers (full_name,email,phone,city) VALUES (?,?,?,?)", (request.form["full_name"].strip(), request.form["email"].strip(), request.form.get("phone", "").strip(), request.form.get("city", "").strip()))
            flash("Customer added.", "success")
        except Exception:
            flash("Could not add customer; verify required fields and unique email.", "danger")
        return redirect(url_for("customers.index"))
    term = request.args.get("q", "").strip()
    rows = query_all("SELECT * FROM customers WHERE full_name LIKE ? OR email LIKE ? ORDER BY customer_id DESC", (f"%{term}%", f"%{term}%"))
    return render_template("customers/index.html", customers=rows, term=term)

@bp.route("/<int:customer_id>/edit", methods=("GET", "POST"))
@role_required("ADMIN")
def edit(customer_id):
    customer = query_one("SELECT * FROM customers WHERE customer_id=?", (customer_id,))
    if not customer: return ("Not found", 404)
    if request.method == "POST":
        execute("UPDATE customers SET full_name=?,email=?,phone=?,city=? WHERE customer_id=?", (request.form["full_name"], request.form["email"], request.form.get("phone"), request.form.get("city"), customer_id))
        flash("Customer updated.", "success"); return redirect(url_for("customers.index"))
    return render_template("customers/edit.html", customer=customer)

@bp.post("/<int:customer_id>/delete")
@role_required("ADMIN")
def delete(customer_id):
    execute("DELETE FROM customers WHERE customer_id=?", (customer_id,)); flash("Customer deleted.", "info")
    return redirect(url_for("customers.index"))

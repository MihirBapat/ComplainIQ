"""Account CRUD routes."""
from flask import Blueprint, flash, redirect, render_template, request, url_for
from app.auth import role_required
from app.db import execute, query_all
bp = Blueprint("accounts", __name__, url_prefix="/accounts")
@bp.route("", methods=("GET","POST"))
@role_required("ADMIN")
def index():
    if request.method == "POST":
        try:
            execute("INSERT INTO accounts (customer_id,type_id,account_number) VALUES (?,?,?)", (request.form["customer_id"],request.form["type_id"],request.form["account_number"]))
            flash("Account added.","success")
        except Exception: flash("Could not add account.","danger")
        return redirect(url_for("accounts.index"))
    return render_template("accounts/index.html", accounts=query_all("SELECT a.*,c.full_name,t.type_name FROM accounts a JOIN customers c ON c.customer_id=a.customer_id JOIN account_types t ON t.type_id=a.type_id ORDER BY a.account_id DESC"), customers=query_all("SELECT customer_id,full_name FROM customers ORDER BY full_name"), types=query_all("SELECT * FROM account_types"))

@bp.post("/<int:account_id>/delete")
@role_required("ADMIN")
def delete(account_id):
    execute("DELETE FROM accounts WHERE account_id=?", (account_id,)); flash("Account deleted.", "info")
    return redirect(url_for("accounts.index"))

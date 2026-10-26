"""Account CRUD routes."""
from flask import Blueprint, flash, redirect, render_template, request, url_for
from app.auth import role_required
from app.db import execute, query_all, query_one
bp = Blueprint("accounts", __name__, url_prefix="/accounts")
@bp.route("", methods=("GET","POST"))
@role_required("ADMIN")
def index():
    if request.method == "POST":
        try:
            execute("INSERT INTO accounts (customer_id,type_id,account_number,status) VALUES (?,?,?,?)", (request.form["customer_id"],request.form["type_id"],request.form["account_number"].strip(), request.form.get("status", "ACTIVE")))
            flash("Account added.","success")
        except Exception: flash("Could not add account.","danger")
        return redirect(url_for("accounts.index"))
    return render_template("accounts/index.html", accounts=query_all("SELECT a.*,c.full_name,t.type_name FROM accounts a JOIN customers c ON c.customer_id=a.customer_id JOIN account_types t ON t.type_id=a.type_id ORDER BY a.account_id DESC"), customers=query_all("SELECT customer_id,full_name FROM customers ORDER BY full_name"), types=query_all("SELECT * FROM account_types"))

@bp.route("/<int:account_id>/edit", methods=("GET", "POST"))
@role_required("ADMIN")
def edit(account_id):
    account = query_one("SELECT * FROM accounts WHERE account_id=?", (account_id,))
    if not account:
        return ("Account not found", 404)
    if request.method == "POST":
        try:
            execute("UPDATE accounts SET customer_id=?, type_id=?, account_number=?, status=? WHERE account_id=?", (
                request.form["customer_id"], request.form["type_id"], request.form["account_number"].strip(), request.form["status"], account_id))
            flash("Account updated.", "success")
            return redirect(url_for("accounts.index"))
        except Exception:
            flash("Could not update account. Check the account number is unique.", "danger")
    return render_template("accounts/edit.html", account=account,
                           customers=query_all("SELECT customer_id,full_name FROM customers ORDER BY full_name"),
                           types=query_all("SELECT * FROM account_types"))

@bp.post("/<int:account_id>/delete")
@role_required("ADMIN")
def delete(account_id):
    execute("DELETE FROM accounts WHERE account_id=?", (account_id,)); flash("Account deleted.", "info")
    return redirect(url_for("accounts.index"))

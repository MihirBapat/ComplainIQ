"""Transaction listing and creation."""
from flask import Blueprint, flash, redirect, render_template, request, url_for
from app.auth import role_required
from app.db import execute, query_all
from app.services.fraud_rules import run_rules
bp = Blueprint("transactions", __name__, url_prefix="/transactions")
@bp.route("", methods=("GET","POST"))
@role_required("ADMIN")
def index():
    if request.method == "POST":
        try:
            cursor=execute("INSERT INTO transactions (account_id,txn_type,amount,merchant,location) VALUES (?,?,?,?,?)",(request.form["account_id"],request.form["txn_type"],float(request.form["amount"]),request.form.get("merchant"),request.form.get("location")))
            flags=run_rules(cursor.lastrowid); flash("Transaction added." + (" Flags: "+", ".join(flags) if flags else ""),"success")
        except (ValueError, KeyError): flash("Enter a valid positive transaction amount.","danger")
        return redirect(url_for("transactions.index"))
    account = request.args.get("account_id", "")
    status = request.args.get("status", "")
    txn_type = request.args.get("txn_type", "")
    date_from = request.args.get("date_from", "")
    date_to = request.args.get("date_to", "")
    sql = """SELECT t.*,a.account_number FROM transactions t JOIN accounts a ON a.account_id=t.account_id
             WHERE (?='' OR t.account_id=?) AND (?='' OR t.status=?) AND (?='' OR t.txn_type=?)
             AND (?='' OR date(t.txn_time)>=date(?)) AND (?='' OR date(t.txn_time)<=date(?))
             ORDER BY t.txn_time DESC, t.txn_id DESC LIMIT 300"""
    rows=query_all(sql,(account,account,status,status,txn_type,txn_type,date_from,date_from,date_to,date_to))
    return render_template("transactions/index.html", transactions=rows, accounts=query_all("SELECT account_id,account_number FROM accounts ORDER BY account_number"), selected_account=account, selected_status=status, selected_type=txn_type, date_from=date_from, date_to=date_to)

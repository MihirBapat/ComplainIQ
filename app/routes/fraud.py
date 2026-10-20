from flask import Blueprint,flash,redirect,render_template,url_for
from app.auth import role_required
from app.db import execute,query_all
bp=Blueprint("fraud",__name__,url_prefix="/fraud")
@bp.get("")
@role_required("ADMIN","AGENT")
def index(): return render_template("fraud/index.html",flags=query_all("SELECT * FROM v_fraud_dashboard WHERE status='PENDING' ORDER BY created_at DESC"))
@bp.post("/<int:flag_id>/<status>")
@role_required("ADMIN","AGENT")
def review(flag_id,status):
    if status in ("CONFIRMED","DISMISSED"): execute("UPDATE fraud_flags SET status=?,reviewed_by=? WHERE flag_id=?",(status,None,flag_id)); flash("Flag reviewed.","success")
    return redirect(url_for("fraud.index"))

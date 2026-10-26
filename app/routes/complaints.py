"""Public complaint submission and staff review workflow."""
from flask import Blueprint, flash, redirect, render_template, request, url_for
from app.auth import role_required
from app.db import execute, query_all, query_one
from app.services.nlp_service import predict
bp=Blueprint("complaints",__name__,url_prefix="/complaints")

@bp.route("/new",methods=("GET","POST"),endpoint="new")
def new():
    if request.method=="POST":
        customer=query_one("SELECT c.*,a.account_id FROM customers c JOIN accounts a ON a.customer_id=c.customer_id WHERE c.email=? AND a.account_number=?",(request.form.get("email"),request.form.get("account_number")))
        text=request.form.get("complaint_text",""); txn_id=request.form.get("txn_id") or None
        if not customer or len(text.strip())<20: flash("Use a registered email/account and at least 20 characters.","danger"); return redirect(url_for("complaints.new"))
        transaction = None
        if txn_id:
            transaction = query_one("SELECT amount FROM transactions WHERE txn_id=? AND account_id=?", (txn_id, customer["account_id"]))
            if not transaction:
                flash("That transaction does not belong to this account.", "danger")
                return redirect(url_for("complaints.new"))
        amount = transaction["amount"] if transaction else None
        result=predict(text,amount); category=query_one("SELECT category_id FROM complaint_categories WHERE name=?",(result["category"],))["category_id"]
        status="IN_REVIEW" if result["confidence"]<.45 else "OPEN"
        execute("INSERT INTO complaints (customer_id,account_id,txn_id,complaint_text,status,category_id,confidence,sentiment_score,sentiment_label,urgency,model_id) VALUES (?,?,?,?,?,?,?,?,?,?,?)",(customer["customer_id"],customer["account_id"],txn_id,text,status,category,result["confidence"],result["sentiment_score"],result["sentiment_label"],result["urgency"],result["model_id"]))
        flash(f"Complaint submitted. Predicted {result['category']}; urgency {result['urgency']}.","success"); return redirect(url_for("complaints.new"))
    return render_template("complaints/new.html")

@bp.get("")
@role_required("ADMIN","AGENT")
def index():
    status = request.args.get("status", "")
    category = request.args.get("category_id", "")
    urgency = request.args.get("urgency", "")
    sentiment = request.args.get("sentiment", "")
    complaints = query_all("""SELECT * FROM v_complaint_overview
        WHERE (?='' OR status=?) AND (?='' OR category_id=?) AND (?='' OR urgency=?) AND (?='' OR sentiment_label=?)
        ORDER BY submitted_at DESC, complaint_id DESC""", (status,status,category,category,urgency,urgency,sentiment,sentiment))
    return render_template("complaints/index.html", complaints=complaints, categories=query_all("SELECT * FROM complaint_categories"), filters={"status":status,"category_id":category,"urgency":urgency,"sentiment":sentiment})

@bp.route("/<int:complaint_id>",methods=("GET","POST"))
@role_required("ADMIN","AGENT")
def detail(complaint_id):
    if request.method=="POST":
        execute("UPDATE complaints SET status=?,category_id=? WHERE complaint_id=?",(request.form["status"],request.form["category_id"],complaint_id)); execute("INSERT INTO complaint_actions (complaint_id,staff_id,action,note) VALUES (?,?,?,?)",(complaint_id,request.form.get("staff_id") or None,"NOTE",request.form.get("note")))
        flash("Complaint updated.","success"); return redirect(url_for("complaints.detail",complaint_id=complaint_id))
    return render_template("complaints/detail.html",complaint=query_one("SELECT * FROM v_complaint_overview WHERE complaint_id=?",(complaint_id,)),categories=query_all("SELECT * FROM complaint_categories"),actions=query_all("SELECT * FROM complaint_actions WHERE complaint_id=? ORDER BY acted_at DESC",(complaint_id,)),flags=query_all("SELECT * FROM fraud_flags WHERE complaint_id=?",(complaint_id,)))

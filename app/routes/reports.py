from flask import Blueprint,render_template
from app.auth import role_required
from app.db import query_all
bp=Blueprint("reports",__name__,url_prefix="/reports")
@bp.get("")
@role_required("ADMIN","AGENT")
def index():
    return render_template("reports/index.html",top=query_all("SELECT cu.full_name,COUNT(*) count FROM customers cu JOIN complaints c ON c.customer_id=cu.customer_id GROUP BY cu.customer_id ORDER BY count DESC LIMIT 10"),flags=query_all("SELECT * FROM v_fraud_dashboard ORDER BY created_at DESC LIMIT 50"))

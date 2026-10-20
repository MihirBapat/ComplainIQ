from flask import Blueprint,render_template,request
from app.auth import role_required
from app.services.nlp_service import predict
bp=Blueprint("model_info",__name__,url_prefix="/model")
@bp.route("",methods=("GET","POST"))
@role_required("ADMIN")
def index():
    result=None
    if request.method=="POST": result=predict(request.form.get("text","This is a sufficiently long complaint text."))
    return render_template("model/index.html",result=result)

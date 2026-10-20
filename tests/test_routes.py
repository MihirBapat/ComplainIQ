"""Core authentication and CRUD route tests."""
from app import create_app
from app.db import init_db
from werkzeug.security import generate_password_hash

def test_login_and_customer_crud(tmp_path):
    app=create_app({"TESTING":True,"DATABASE":tmp_path/"routes.db","SECRET_KEY":"test"}); init_db(app)
    with app.app_context():
        from app.db import execute
        execute("INSERT INTO staff (username,password_hash,role) VALUES (?,?,?)",("admin",generate_password_hash("pw"),"ADMIN"))
    client=app.test_client(); assert client.get("/customers").status_code==302
    assert client.post("/login",data={"username":"admin","password":"pw"}).status_code==302
    assert client.post("/customers",data={"full_name":"Ada","email":"ada@example.com","phone":"","city":"Delhi"}).status_code==302
    assert b"Ada" in client.get("/customers").data
    assert client.post("/customers/1/delete").status_code==302

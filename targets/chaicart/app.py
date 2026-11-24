"""
ChaiCart — a DELIBERATELY VULNERABLE demo shop for testing Trinetra.
DO NOT deploy. Every VULN comment marks a planted flaw Trinetra must find.
"""
import os
import sqlite3
from flask import Flask, request, session, jsonify, render_template_string

app = Flask(__name__)
# VULN (secret): hardcoded secret key committed in source
app.secret_key = "sk_live_hardcoded_dev_key_do_not_ship_12345"

DB = os.path.join(os.path.dirname(__file__), "chaicart.db")


def db():
    c = sqlite3.connect(DB)
    c.row_factory = sqlite3.Row
    return c


def init_db():
    if os.path.exists(DB):
        os.remove(DB)
    c = db()
    c.executescript(
        """
        CREATE TABLE users(id INTEGER PRIMARY KEY, username TEXT, password TEXT, role TEXT, api_key TEXT);
        CREATE TABLE orders(id INTEGER PRIMARY KEY, user_id INTEGER, item TEXT, amount REAL);
        CREATE TABLE products(id INTEGER PRIMARY KEY, name TEXT, price REAL);
        """
    )
    c.execute("INSERT INTO users VALUES(1,'alice','alicepass','user','key_alice_123')")
    c.execute("INSERT INTO users VALUES(2,'bob','bobpass','user','key_bob_456')")
    c.execute("INSERT INTO users VALUES(3,'admin','supersecret','admin','key_admin_789')")
    c.execute("INSERT INTO orders VALUES(1001,1,'Masala Chai x100',4999.0)")
    c.execute("INSERT INTO orders VALUES(1002,2,'Private Bob Order - Saffron',8999.0)")
    c.execute("INSERT INTO products VALUES(1,'Premium Tea Set',2500.0)")
    c.commit()
    c.close()


@app.route("/login", methods=["POST"])
def login():
    u = request.form.get("username", "")
    p = request.form.get("password", "")
    c = db()
    # VULN (sqli): query built by string-formatting user input
    # VULN (rate-limit): no throttling on login attempts
    q = "SELECT * FROM users WHERE username='%s' AND password='%s'" % (u, p)
    row = c.execute(q).fetchone()
    c.close()
    if row:
        session["user_id"] = row["id"]
        session["role"] = row["role"]
        return jsonify(ok=True, user=row["username"], role=row["role"])
    return jsonify(ok=False), 401


@app.route("/signup", methods=["POST"])
def signup():
    u = request.form.get("username", "")
    p = request.form.get("password", "")
    # VULN (mass-assignment): role is taken straight from client input
    role = request.form.get("role", "user")
    c = db()
    c.execute(
        "INSERT INTO users(username,password,role,api_key) VALUES(?,?,?,?)",
        (u, p, role, "key_new"),
    )
    c.commit()
    c.close()
    return jsonify(ok=True, username=u, role=role)


@app.route("/order/<int:oid>")
def order(oid):
    if "user_id" not in session:
        return jsonify(error="login required"), 401
    c = db()
    row = c.execute("SELECT * FROM orders WHERE id=?", (oid,)).fetchone()
    c.close()
    if not row:
        return jsonify(error="not found"), 404
    # VULN (idor): no check that the order belongs to the logged-in user
    return jsonify(id=row["id"], user_id=row["user_id"], item=row["item"], amount=row["amount"])


@app.route("/admin")
def admin():
    # VULN (access-control): admin panel has no auth/role check
    c = db()
    users = [dict(r) for r in c.execute("SELECT id,username,role,api_key FROM users").fetchall()]
    c.close()
    return jsonify(panel="admin", users=users)


@app.route("/checkout", methods=["POST"])
def checkout():
    # VULN (price-tampering): trusts a client-supplied price
    # VULN (negative-qty): no validation that qty is a positive integer
    price = float(request.form.get("price", 0))
    qty = int(request.form.get("qty", 1))
    total = price * qty
    return jsonify(ok=True, price=price, qty=qty, total=total)


@app.route("/search")
def search():
    q = request.args.get("q", "")
    # VULN (xss): user input reflected into HTML without escaping
    return "<html><body><h3>Results for %s</h3></body></html>" % q


@app.route("/greet")
def greet():
    name = request.args.get("name", "guest")
    # VULN (ssti): user input is rendered as a Jinja template (not just data)
    return render_template_string("Hi " + name)


if __name__ == "__main__":
    init_db()
    # VULN (debug): debug mode exposes the Werkzeug console in production
    app.run(host="127.0.0.1", port=5001, debug=True, use_reloader=False)

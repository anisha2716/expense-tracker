from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "smartspend_secret"

# ---------- DATABASE INIT ----------
def init_db():
    conn = sqlite3.connect("expenses.db")
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE,
        password TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS expenses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_email TEXT,
        name TEXT,
        amount REAL
    )
    """)

    conn.commit()
    conn.close()

init_db()

# ---------- HOME ----------
@app.route("/")
def home():
    if "user" not in session:
        return redirect("/login")

    conn = sqlite3.connect("expenses.db")
    cur = conn.cursor()

    cur.execute("SELECT name, amount FROM expenses WHERE user_email=?",
                (session["user"],))
    data = cur.fetchall()

    total = sum([i[1] for i in data])

    conn.close()

    return render_template("index.html", expenses=data, total=total)

# ---------- REGISTER ----------
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        conn = sqlite3.connect("expenses.db")
        cur = conn.cursor()

        try:
            cur.execute("INSERT INTO users (email, password) VALUES (?,?)",
                        (email, password))
            conn.commit()
        except:
            pass

        conn.close()
        return redirect("/login")

    return render_template("signup.html")

# ---------- LOGIN ----------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        conn = sqlite3.connect("expenses.db")
        cur = conn.cursor()

        cur.execute("SELECT * FROM users WHERE email=? AND password=?",
                    (email, password))
        user = cur.fetchone()

        conn.close()

        if user:
            session["user"] = email
            return redirect("/")
        else:
            return "Invalid login"

    return render_template("login.html")

# ---------- ADD EXPENSE ----------
@app.route("/add", methods=["POST"])
def add():
    if "user" not in session:
        return redirect("/login")

    name = request.form["name"]
    amount = request.form["amount"]

    conn = sqlite3.connect("expenses.db")
    cur = conn.cursor()

    cur.execute("INSERT INTO expenses (user_email, name, amount) VALUES (?,?,?)",
                (session["user"], name, amount))

    conn.commit()
    conn.close()

    return redirect("/")

# ---------- LOGOUT ----------
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


if __name__ == "__main__":
    app.run(debug=True)

from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(__name__)
app.secret_key = "smartspend"

# HOME
@app.route('/', methods=['GET', 'POST'])
def home():

    if 'user' not in session:
        return redirect('/login')

    conn = sqlite3.connect('expenses.db')
    cur = conn.cursor()

    if request.method == 'POST':
        title = request.form['title']
        amount = float(request.form['amount'])
        category = request.form['category']

        cur.execute("""
        INSERT INTO expenses (user, title, amount, category)
        VALUES (?, ?, ?, ?)
        """, (session['user'], title, amount, category))

        conn.commit()

    cur.execute("SELECT * FROM expenses WHERE user=?", (session['user'],))
    expenses = cur.fetchall()

    total = 0

    category_totals = {
        "Food": 0,
        "Travel": 0,
        "Shopping": 0,
        "Bills": 0,
        "Entertainment": 0,
        "Fuel": 0,
        "Others": 0
    }

    for e in expenses:
        total += e[3]
        if e[4] in category_totals:
            category_totals[e[4]] += e[3]

    highest_category = max(category_totals, key=category_totals.get)

    conn.close()

    return render_template(
        "index.html",
        expenses=expenses,
        total=total,
        category_totals=category_totals,
        highest_category=highest_category
    )


# SIGNUP
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect('expenses.db')
        cur = conn.cursor()

        try:
            cur.execute("INSERT INTO users (username, password) VALUES (?, ?)",
                        (username, password))
            conn.commit()
        except:
            return "User exists"

        conn.close()
        return redirect('/login')

    return render_template('signup.html')


# LOGIN
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect('expenses.db')
        cur = conn.cursor()

        cur.execute("SELECT * FROM users WHERE username=? AND password=?",
                    (username, password))

        user = cur.fetchone()
        conn.close()

        if user:
            session['user'] = username
            return redirect('/')

        return "Invalid login"

    return render_template('login.html')


# LOGOUT
@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/login')


# DELETE
@app.route('/delete/<int:id>')
def delete(id):

    if 'user' not in session:
        return redirect('/login')

    conn = sqlite3.connect('expenses.db')
    cur = conn.cursor()

    cur.execute("DELETE FROM expenses WHERE id=? AND user=?",
                (id, session['user']))

    conn.commit()
    conn.close()

    return redirect('/')


if __name__ == '__main__':
    app.run(debug=True)
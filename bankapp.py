from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace with a secure key

# Function to initialize the database
def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            age INTEGER NOT NULL,
            gender TEXT NOT NULL,
            password TEXT NOT NULL,
            balance REAL DEFAULT 0
        )
    ''')
    conn.commit()
    conn.close()

# Route to render the index page
@app.route('/')
def index():
    return render_template('index.html')

# Route to render the registration form and handle registration
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        age = request.form['age']
        gender = request.form['gender']
        password = request.form['password']

        # Store user data in SQLite database
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute("INSERT INTO users (name, age, gender, password, balance) VALUES (?, ?, ?, ?, ?)",
                  (name, age, gender, password, 0))
        conn.commit()
        conn.close()

        flash('Registration successful. Please log in.')
        return redirect(url_for('login'))
    return render_template('register.html')

# Route to render the login form and handle login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Check if username and password match
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE name=? AND password=?", (username, password))
        user = c.fetchone()
        conn.close()

        if user:
            flash('Login successful.')
            return redirect(url_for('dashboard', username=username))
        else:
            flash('Invalid username or password. Please try again.')
            return render_template('login.html')
    return render_template('login.html')


# Route to render the dashboard with user details
@app.route('/dashboard/<username>')
def dashboard(username):
    # Retrieve user data from the database
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE name=?", (username,))
    user = c.fetchone()
    conn.close()

    return render_template('dashboard.html', user=user)

# Route to handle depositing money
@app.route('/deposit/<username>', methods=['POST'])
def deposit(username):
    amount = float(request.form['amount'])

    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("UPDATE users SET balance = balance + ? WHERE name = ?", (amount, username))
    conn.commit()
    conn.close()

    flash('Deposit successful.')
    return redirect(url_for('dashboard', username=username))

# Route to handle withdrawing money
@app.route('/withdraw/<username>', methods=['POST'])
def withdraw(username):
    amount = float(request.form['amount'])

    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT balance FROM users WHERE name=?", (username,))
    balance = c.fetchone()[0]

    if balance >= amount:
        c.execute("UPDATE users SET balance = balance - ? WHERE name = ?", (amount, username))
        conn.commit()
        conn.close()
        flash('Withdrawal successful.')
        return redirect(url_for('dashboard', username=username))
    else:
        conn.close()
        flash('Insufficient balance.')
        return redirect(url_for('dashboard', username=username))

if __name__ == '__main__':
    init_db()  # Initialize the database
    app.run(debug=True)

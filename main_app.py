from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from cryptography.fernet import Fernet
import os
import secrets
import string

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


def init_db():
    conn = sqlite3.connect('passwords.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY, username TEXT UNIQUE, password TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS passwords
                 (id INTEGER PRIMARY KEY, user_id INTEGER, site TEXT, username TEXT, encrypted_password TEXT, notes TEXT)''')
    conn.commit()
    conn.close()

class User(UserMixin):
    def __init__(self, id, username):
        self.id = id
        self.username = username

@login_manager.user_loader
def load_user(user_id):
    conn = sqlite3.connect('passwords.db')
    c = conn.cursor()
    c.execute("SELECT id, username FROM users WHERE id=?", (user_id,))
    user = c.fetchone()
    conn.close()
    if user:
        return User(user[0], user[1])
    return None

def get_encryption_key():
    key_file = 'secret.key'
    if not os.path.exists(key_file):
        key = Fernet.generate_key()
        with open(key_file, 'wb') as f:
            f.write(key)
    else:
        with open(key_file, 'rb') as f:
            key = f.read()
    return key

fernet = Fernet(get_encryption_key())

def generate_password(length=16):
    characters = string.ascii_letters + string.digits + string.punctuation
    return ''.join(secrets.choice(characters) for _ in range(length))

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_pw = generate_password_hash(password)
        conn = sqlite3.connect('passwords.db')
        c = conn.cursor()
        try:
            c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_pw))
            conn.commit()
            flash('Registration successful! Please login.')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Username already exists.')
        finally:
            conn.close()
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = sqlite3.connect('passwords.db')
        c = conn.cursor()
        c.execute("SELECT id, password FROM users WHERE username=?", (username,))
        user = c.fetchone()
        conn.close()
        if user and check_password_hash(user[1], password):
            session['user_id'] = user[0]
            user_obj = User(user[0], username)
            login_user(user_obj)
            flash('Login successful!')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid credentials.')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    session.pop('user_id', None)
    flash('Logged out.')
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    conn = sqlite3.connect('passwords.db')
    c = conn.cursor()
    c.execute("SELECT id, site, username, encrypted_password, notes FROM passwords WHERE user_id=?", (current_user.id,))
    entries = []
    for row in c.fetchall():
        try:
            decrypted_pw = fernet.decrypt(row[3].encode()).decode()
        except:
            decrypted_pw = "Decryption error"
        entries.append((row[0], row[1], row[2], decrypted_pw, row[4]))
    conn.close()
    return render_template('dashboard.html', entries=entries)

@app.route('/add_password', methods=['GET', 'POST'])
@login_required
def add_password():
    if request.method == 'POST':
        site = request.form['site']
        username = request.form['username']
        password = request.form['password']
        notes = request.form['notes']
        encrypted_pw = fernet.encrypt(password.encode()).decode()
        conn = sqlite3.connect('passwords.db')
        c = conn.cursor()
        c.execute("INSERT INTO passwords (user_id, site, username, encrypted_password, notes) VALUES (?, ?, ?, ?, ?)",
                  (current_user.id, site, username, encrypted_pw, notes))
        conn.commit()
        conn.close()
        flash('Password added successfully.')
        return redirect(url_for('dashboard'))
    return render_template('add_password.html')

@app.route('/delete_password/<int:id>')
@login_required
def delete_password(id):
    conn = sqlite3.connect('passwords.db')
    c = conn.cursor()
    c.execute("DELETE FROM passwords WHERE id=? AND user_id=?", (id, current_user.id))
    conn.commit()
    conn.close()
    flash('Password deleted.')
    return redirect(url_for('dashboard'))

@app.route('/generate')
@login_required
def generate():
    pw = generate_password()
    return render_template('generate.html', password=pw)

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)

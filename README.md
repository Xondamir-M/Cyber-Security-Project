# Password Manager

## Quick Start
1. `cd password_manager`
2. `python3 app.py`
3. Visit: `http://127.0.0.1:5000`

**Required dependencies**: _Flask, Flask-Login, cryptography, Werkzeug_. Install via `pip install flask flask-login cryptography werkzeug`).

## Features

- Secure login with password hashing + salting
- Uses Fernet (symmetric encryption) from `cryptography`
- Strong random password generation
- View, add, and delete passwords
- Protection against SQL injection, proper session handling

## Technologies Used

- Python + Flask
- Flask-Login + Werkzeug
- SQLite
- `cryptography` (Fernet)
- HTML + CSS (Jinja2 templates)

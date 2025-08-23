from flask import Flask, request, jsonify, redirect, make_response
import sqlite3
import hashlib
import uuid

app = Flask(__name__)
app.secret_key = "une_cle_secrete_pour_session"

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def check_user(username, password):
    conn = sqlite3.connect("music.db")
    c = conn.cursor()
    c.execute("SELECT password_hash FROM users WHERE username=?", (username,))
    row = c.fetchone()
    conn.close()
    if row and row[0] == hash_password(password):
        return True
    return False

@app.route("/auth/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        data = request.form
        username = data.get("username")
        password = data.get("password")
        if check_user(username, password):
            resp = make_response(redirect("/"))
            resp.set_cookie("session_id", str(uuid.uuid4()))
            return resp
        else:
            return "Identifiants invalides", 401
    # HTML du login avec lien vers register
    return '''
    <form method="post">
      <input name="username" placeholder="Username"/>
      <input name="password" type="password" placeholder="Password" type="password"/>
      <button type="submit">Login</button>
    </form>
    <p>Pas encore de compte ? <a href="/auth/register">Inscrivez-vous ici</a></p>
    '''

@app.route("/auth/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        data = request.form
        username = data.get("username")
        password = data.get("password")
        conn = sqlite3.connect("music.db")
        c = conn.cursor()
        try:
            c.execute(
                "INSERT INTO users (username, password_hash) VALUES (?, ?)",
                (username, hash_password(password))
            )
            conn.commit()
        except sqlite3.IntegrityError:
            conn.close()
            return "Nom d'utilisateur déjà utilisé", 400
        conn.close()
        return redirect("/auth/login")
    # HTML du register
    return '''
    <form method="post">
      <input name="username" placeholder="Username"/>
      <input name="password" type="password" placeholder="Password"/>
      <button type="submit">Register</button>
    </form>
    '''

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000)

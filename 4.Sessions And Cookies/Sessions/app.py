from flask import Flask, session, redirect, url_for, request, render_template

app = Flask(__name__)
app.secret_key = "secret"

@app.route('/')
def home():
    if 'user' in session:
        return f"Welcome back, {session['user']}!"
    return "You are not logged in."

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        session['user'] = request.form['username']
        return redirect(url_for('home'))
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
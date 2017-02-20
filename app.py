from flask import Flask, render_template, request,redirect, url_for, session, flash
import os, settings, sqlite3, time

app = Flask(__name__)
app.config.update(
    DATABASE=settings.DATABASE,
    DEBUG=False,
    SECRET_KEY=settings.SECRET_KEY,
)

os.environ['TZ'] = 'Europe/Belgrade'
database = sqlite3.connect(app.config['DATABASE'])
cursor = database.cursor()
defaultsettings = cursor.execute("SELECT * FROM Settings ORDER BY ID DESC LIMIT 1").fetchone()
app.config.update(
    REMINDER=defaultsettings[1]
)

def is_logged_in(session):
    return (('pw' in session) and (session['pw'] == settings.PASSWORD))

def do_a_magic():
    return "Haha"

@app.route('/login', methods=['POST', 'GET'])
def login():
    if is_logged_in(session):
        return redirect(url_for('home'))
    else:
        error = None
        if request.method == 'POST':
            if request.form['password'] == settings.PASSWORD:
                session['pw'] = settings.PASSWORD
                return redirect(url_for('home'))
            else:
                error = "Incorrect password"
        return render_template('login.html', error=error)
        
        
@app.route('/home', methods=['POST', 'GET'])
def home():
    if is_logged_in(session):
        if request.method == 'POST':
            currenttime = time.strftime("%c")
            cursor.execute('INSERT INTO Queries(QUERY, DATETIME) VALUES (?, ?)', (request.form['query'], currenttime,))
            database.commit()
            if 'SELECT' in request.form['query'].upper():
                session['query'] = request.form['query']
                return redirect(url_for('show'))
            try:
                cursor.execute(request.form['query'])
                cursor.execute('UPDATE Queries SET SUCCEEDED=1 WHERE DATETIME = ?', (currenttime,))
                database.commit()
                flash('Database updated successfully', 'success')
            except sqlite3.Error, e:
                flash(e.args[0], 'error')
        lattest_queries = cursor.execute('SELECT * FROM Queries ORDER BY ID DESC LIMIT 15').fetchall()
        return render_template('home.html', lattest_queries=lattest_queries, reminder=app.config['REMINDER'])
    else:
        return redirect(url_for('login'))
        
@app.route("/logout")
def logout():
    if is_logged_in(session):
        session.pop('pw', None)
    return redirect(url_for('login'))

@app.route('/show')
def show():
    if 'query' in session:
        header = None
        data = None
        error = None
        try:
            header = database.execute(session['query']).description
            data = cursor.execute(session['query']).fetchall()
            cursor.execute('UPDATE Queries SET SUCCEEDED=1 WHERE ID = (SELECT ID FROM Queries ORDER BY ID DESC LIMIT 1)')
            database.commit()
        except sqlite3.Error, e:
            flash(e.args[0], 'error')
            return redirect(url_for('home'))
        return render_template('show.html', header=header, data=data, error=error)
    else:
        return 'You haven\'t done any query yet!'

@app.route('/')
def main():
    return redirect(url_for('login'))

app.run(host=os.getenv('IP', '0.0.0.0'),port=int(os.getenv('PORT', 8080)))

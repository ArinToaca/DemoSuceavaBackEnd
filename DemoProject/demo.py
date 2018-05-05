import os
import sys
import sqlite3
from flask import jsonify
from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash

app = Flask(__name__)  # create the application instance :)
app.config.from_object(__name__)  # load config from this file , flaskr.py

# Load default config and override config from an environment variable
app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'suceavabackend.db'),
    SECRET_KEY='development key',
    USERNAME='admin',
    PASSWORD='default'
))
app.config.from_envvar('FLASKR_SETTINGS', silent=True)


def init_db():
    db = get_db()
    with app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()


def connect_db():
    """Connects to the specific database."""
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv


@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()


def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db

# ROUTES


@app.route('/data', methods=['POST', 'GET'])
def get_or_show_data():
    db = get_db()
    if request.method == 'POST':
        db.execute('insert into entries (timestamp, value) values (?, ?)',
                   [request.form['timestamp'], request.form['value']])
        db.commit()
        flash('New entry was successfully posted')
        return 'OK'
    elif request.method == 'GET':
        cursor = db.execute('select timestamp, value from entries order by '
                            'timestamp asc')
        columns = [column[0] for column in cursor.description]
        results = []
        for row in cursor.fetchall():
            results.append(dict(zip(columns, row)))
        return jsonify(results)


@app.route('/afterdate', methods=['POST'])
def get_latest():
    db = get_db()
    if request.method == 'POST':
        cursor = db.execute('select timestamp, value from entries '
                            'where timestamp  > ?'
                            'order by timestamp asc',
                            [request.form['timestamp']])
        columns = [column[0] for column in cursor.description]
        results = []
        for row in cursor.fetchall():
            results.append(dict(zip(columns, row)))
        return jsonify(results)


if __name__ == '__main__':
    if sys.argv[1] == 'dbinit':
        print("init db")
        with app.app_context():
            init_db()
    elif sys.argv[1] == 'run':
        print('running app...')
        app.run()
    else:
        raise ValueError("incorrect nr of args!")

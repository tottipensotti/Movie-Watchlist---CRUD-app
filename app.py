from flask import Flask
from flask import render_template, request, redirect, url_for
from flask import send_from_directory
from flaskext.mysql import MySQL
from datetime import datetime
import os
import random

app = Flask(__name__)

# database connection
mysql = MySQL()
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = ''
app.config['MYSQL_DATABASE_BD'] = 'watchlist'
mysql.init_app(app)

FOLDER = os.path.join('uploads')
app.config['FOLDER'] = FOLDER

@app.route('/uploads/<posterName>')
def uploads(posterName):
    return send_from_directory(app.config['FOLDER'], posterName)


@app.route('/') # http://127.0.0.1:5000/
def index():
    sql = 'SELECT * FROM `movies`.`watchlist`'
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute(sql)
    movies = cursor.fetchall()
    print(movies)
    conn.commit()
    return render_template('movies/index.html', movies = movies)

@app.route('/create') # http://127.0.0.1:5000/create
def create():
    return render_template('movies/create.html')

@app.route('/update', methods = ['POST'])
def update():
    id = request.form['txtId']
    _name = request.form['txtName']
    _description = request.form['txtDescription']
    _poster = request.files['txtPoster']
    
    data = (_name, _description, id)
    sql = 'UPDATE `movies`.`watchlist` SET `name`= %s, `description`= %s WHERE `id`= %s'

    conn = mysql.connect()
    cursor = conn.cursor()

    now = datetime.now()
    time = now.strftime('%Y%H%M%S')

    if _poster.filename != '':
        newPosterName = time + _poster.filename
        _poster.save('uploads/' + newPosterName)
        cursor.execute('SELECT poster FROM `movies`.`watchlist` WHERE id=%s', id)
        line = cursor.fetchall()

        os.remove(os.path.join(app.config['FOLDER'], line[0][0]))
        cursor.execute('UPDATE `movies`.`watchlist` SET poster=%s WHERE id=%s', (newPosterName, id))
        conn.commit()
        
    cursor.execute(sql, data)
    conn.commit()

    return redirect('/')

@app.route('/destroy/<int:id>')
def destroy(id):
    conn = mysql.connect()
    cursor = conn.cursor()

    cursor.execute('SELECT poster FROM `movies`.`watchlist` WHERE id=%s', id)
    line = cursor.fetchall()
    os.remove(os.path.join(app.config['FOLDER'], line[0][0]))
    
    cursor.execute('DELETE FROM `movies`.`watchlist` WHERE id=%s', (id))
    conn.commit()    
    return redirect('/')

@app.route('/edit/<int:id>')
def edit(id):
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM `movies`.`watchlist` WHERE id=%s', (id))
    movies  = cursor.fetchall()
    conn.commit()
    return render_template('movies/edit.html', movies = movies)

@app.route('/store', methods=['POST'])
def storage():
    sql = 'INSERT INTO `movies`.`watchlist` (`id`, `name`, `description`, `poster`) VALUES (%s, %s,%s, %s);'
    
    _id = random.randint(0, 100)
    _name = request.form['txtName']
    _description = request.form['txtDescription']
    _poster = request.files['txtPoster']

    now = datetime.now()
    time = now.strftime('%Y%H%M%S')
    
    if _poster.filename != '':
        newPosterName = time + _poster.filename
        _poster.save('uploads/'+newPosterName)

    data = (_id, _name, _description, newPosterName)
    
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute(sql, data)
    conn.commit()

    return redirect('/')

if __name__ == '__main__':
    app.run(debug = True)
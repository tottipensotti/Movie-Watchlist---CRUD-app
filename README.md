This project is part of the **Fullstack with Python course** by Agencia de Aprendizaje para la vida in association with the government of the city of Buenos Aires.
The main task was to create a CRUD app about any topics.

Technologies used:<br>

![Python](https://img.shields.io/badge/Python-FFFFFF?style=flat&logo=python)
![Bootstrap](https://img.shields.io/badge/-Bootstrap-FFFFFF?style=flat&logo=bootstrap&logoColor=563D7C)
![Flask](https://img.shields.io/badge/-Flask-FFFFFF?style=flat&logo=flask&logoColor=563D7C)
![SQL](https://img.shields.io/badge/-MySQL-FFFFFF?style=flat&logo=mysql&logoColor=563D7C)

## Quick Video Demo
[WIP - INSERT VIDEO]

## Walkthrough
First, we need to import all the modules for the app to work <br>
```python
from flask import Flask # for the app
from flask import render_template, request, redirect, send_from_directory, url_for # to work with the files and frontend files
from flaskext.mysql import MySQL # to manage the database
from datetime import datetime
import os # to add/delete files from our folders
import random # to generate random IDs
```

Then we need to create the app, the database connection and the folder where we're going to save our images
```python
app = Flask(__name__)
mysql = MySQL()
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = ''
app.config['MYSQL_DATABASE_BD'] = 'watchlist'
mysql.init_app(app)

FOLDER = os.path.join('uploads')
app.config['FOLDER'] = FOLDER
```

Now we are all set to define the ```@app.route()``` and the functions of the app:<br>

**Index** (the home):
```python
@app.route('/')
def index():
    sql = 'SELECT * FROM `movies`.`watchlist`'
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute(sql)
    movies = cursor.fetchall()
    conn.commit()
    return render_template('movies/index.html', movies = movies)
```

**Uploads** to save the images in the directory folder:
```python
@app.route('/uploads/<posterName>')
def uploads(posterName):
    return send_from_directory(app.config['FOLDER'], posterName)
```

**Create** to add new movies:
```python
@app.route('/create')
def create():
    return render_template('movies/create.html')
```

**Storage** to save the created movies in the database:
```python
@app.route('/store', methods=['POST'])
def storage():
    sql = 'INSERT INTO `movies`.`watchlist` (`id`, `name`, `description`, `poster`) VALUES (%s, %s,%s, %s);'
    
    _id = random.randint(0, 100)
    _name = request.form['txtName']
    _description = request.form['txtDescription']
    _poster = request.files['txtPoster']

    now = datetime.now()
    time = now.strftime('%Y%H%M%S') # adding the timestamp to the picture filename to avoid duplicates
    if _poster.filename != '':
        newPosterName = time + _poster.filename
        _poster.save('uploads/'+newPosterName)

    data = (_id, _name, _description, newPosterName)
    
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute(sql, data)
    conn.commit()

    return redirect('/')
```

**Edit** to edit existing movies:
```python
@app.route('/edit/<int:id>')
def edit(id):
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM `movies`.`watchlist` WHERE id=%s', (id))
    movies  = cursor.fetchall()
    conn.commit()
    return render_template('movies/edit.html', movies = movies)
```

**Update** to save in the database the changes made in edit:
```python
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

    now = datetime.now() # using the timestamp we can make each picture file unique
    time = now.strftime('%Y%H%M%S')

    if _poster.filename != '': # first we check if there is already a picture assigned to the movie
        newPosterName = time + _poster.filename
        _poster.save('uploads/' + newPosterName)
        cursor.execute('SELECT poster FROM `movies`.`watchlist` WHERE id=%s', id)
        line = cursor.fetchall()

        os.remove(os.path.join(app.config['FOLDER'], line[0][0])) # we delete the old picture
        cursor.execute('UPDATE `movies`.`watchlist` SET poster=%s WHERE id=%s', (newPosterName, id))
        conn.commit()
        
    cursor.execute(sql, data)
    conn.commit()

    return redirect('/')
```
**Destroy** to delete movies:
```python
@app.route('/destroy/<int:id>')
def destroy(id):
    conn = mysql.connect()
    cursor = conn.cursor()

    cursor.execute('SELECT poster FROM `movies`.`watchlist` WHERE id=%s', id)
    line = cursor.fetchall()
    os.remove(os.path.join(app.config['FOLDER'], line[0][0])) # we need to delete the picture from the directory too
    
    cursor.execute('DELETE FROM `movies`.`watchlist` WHERE id=%s', (id))
    conn.commit()    
    return redirect('/')
```
And finally we initialize the app:
```python
if __name__ == '__main__':
    app.run(debug = True)
```
Now for the html files we are going to use Bootstrap and Jinja.<br>
For the header and the footer we use the command ```{% include 'movies/header.html' %}``` and ```{% include 'movies/footer.html' %}``` so we can mantain the header and footer along all the sections.<br>
For adding each movie to the home page we use the following commands from Jinja:
```html
{% for movie in movies %}
<tr>
  <td>{{ movie[0] }}</td>
  <td>{{ movie[1] }}</td>
  <td>{{ movie[2] }}</td>
  <td><img class="img-thumbnail" width="200" src="uploads/{{ movie[3] }}" alt=""></td>
  <td><a class="btn btn-warning" href="/edit/{{movie[0]}}">Edit</a>  <a class="btn btn-danger" onclick="return confirm('Do you want to delete this movie?')" href="/destroy/{{movie[0]}}">Delete</a></td>
</tr>
{% endfor %}

```
It allows us to go through the movies array and add each one in a new row with the ID (movie[0]), Name (movie[1]), Description (movie[2]) Image (movie[3]), and also the actions buttons for Edit and Delete the movie.

The **create** and **edit** forms are very similar and they follow the same logic and use Bootstrap classes
```html
<!-- Create form -->
<form method="post" action="/store" enctype="multipart/form-data">
  <div class="form-group">
    <label for="txtName">Name:</label>
    <input id="txtName" class="form-control" type="text" name="txtName">
  </div>
  <div class="form-group">
    <label for="txtDescription">Description</label>
    <input id="txtDescription" class="form-control" type="text" name="txtDescription">
  </div>
  <div class="form-group">
    <label for="txtPoster">Poster</label>
    <input id="txtPoster" class="form-control" type="file" name="txtPoster">
  </div>
  <div class="form-group">
    <input type="submit" class="btn btn-success" value="Add Movie">
    <a href="{{url_for('index')}}" class="btn btn-primary">Back</a> <!-- The url_for command from Flask allows us to go back to the home -->
  </div>
</form>
```
```html
<!-- Edit form -->
<form method="post" action="/update" enctype="multipart/form-data">
  <input type="hidden" value="{{ movie[0] }}" name="txtId" id="txtId">
   <div class="form-group">
    <label for="txtName">Name</label>
    <input id="txtName" class="form-control" type="text" name="txtName" value="{{ movie[1] }}">
  </div>
  <div class="form-group">
    <label for="txtDescription">Description</label>
    <input id="txtDescription" class="form-control" type="text" name="txtDescription" value="{{ movie[2] }}">
  </div>
  <div class="form-group">
    <label for="txtPoster">Poster</label>
    <img class="img-thumbnail" width="200" src="{{url_for('uploads', posterName=movie[3]) }}" alt=""> <!-- It runs the upload function updating the movie picture -->
    <input id="txtPoster" class="form-control" type="file" name="txtPoster">
  </div>
  <div class="form-group">
    <input type="submit" class="btn btn-success" value="Modify">
    <a href="{{url_for('index')}}" class="btn btn-primary">Back</a>
  </div>
</form>
```

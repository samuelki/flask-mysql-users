from flask import Flask, render_template, redirect, session, request, flash
from flask_bcrypt import Bcrypt
from mysqlconnection import connectToMySQL
import re
import datetime

mysql = connectToMySQL('friendsdb')

app = Flask(__name__)
bcrypt = Bcrypt(app)
app.secret_key = "9z8asdfh2j2skl"
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')

@app.route('/')
@app.route('/users')
def index():
    # display all the users
    mysql = connectToMySQL('friendsdb')
    all_users = mysql.query_db("SELECT id, first_name, last_name, email, DATE_FORMAT(created_at, '%M %D, %Y') as created_at FROM users;")

    return render_template('index.html', users=all_users)

@app.route('/users/new')
def new():
    # display a form allowing users to create a new user
    return render_template('add_user.html')
    
@app.route('/users/create', methods=['POST'])
def create():
    # insert a new user into db
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    email = request.form['email']

    query = "INSERT INTO users (first_name, last_name, email, created_at, updated_at) VALUES (%(first_name)s, %(last_name)s, %(email)s, NOW(), NOW());"
    data = {
        'first_name': first_name,
        'last_name': last_name,
        'email': email
    }
    mysql = connectToMySQL('friendsdb')
    mysql.query_db(query, data)

    query = "SELECT id FROM users WHERE first_name=%(first_name)s AND last_name=%(last_name)s AND email=%(email)s;"
    mysql = connectToMySQL('friendsdb')
    id = mysql.query_db(query, data)

    return redirect('/users/'+str(id[0]['id']))

@app.route('/users/<id>')
def show(id):
    # display the info for a particular user with given id
    query = "SELECT * FROM users WHERE id=%(id)s;"
    data = {'id': id}
    mysql = connectToMySQL('friendsdb')
    user = mysql.query_db(query, data)

    return render_template('show_user.html', user=user)

@app.route('/users/<id>/edit')
def edit(id):
    # display a form allowing users to edit an existing user with the given id
    query = "SELECT first_name, last_name, email FROM users WHERE id=%(id)s;"
    data = {'id': id}
    mysql = connectToMySQL('friendsdb')
    user = mysql.query_db(query, data)

    return render_template('edit_user.html', id=id, user=user[0])

@app.route('/users/<id>', methods=['POST'])
def update(id):
    # process the submitted form sent from /users/<id>/edit
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    email = request.form['email']

    query = "UPDATE users SET first_name=%(first_name)s, last_name=%(last_name)s, email=%(email)s, updated_at=NOW() WHERE id=%(id)s"
    data = {
        'id': id,
        'first_name': first_name,
        'last_name': last_name,
        'email': email
    }
    mysql = connectToMySQL('friendsdb')
    mysql.query_db(query, data)

    return redirect('/users/'+str(id))

@app.route('/users/<id>/destroy')
def destroy(id):
    # remove a particular user with the given id
    delete_query = "DELETE FROM users WHERE id=%(id)s;"
    data = {'id': id}
    mysql = connectToMySQL('friendsdb')
    mysql.query_db(delete_query, data)

    return redirect('/users')

if __name__=="__main__":
    app.run(debug=True)
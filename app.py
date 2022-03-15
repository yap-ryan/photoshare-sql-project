######################################
# author ben lawson <balawson@bu.edu>
# Edited by: Craig Einstein <einstein@bu.edu>
######################################
# Some code adapted from
# CodeHandBook at http://codehandbook.org/python-web-application-development-using-flask-and-mysql/
# and MaxCountryMan at https://github.com/maxcountryman/flask-login/
# and Flask Offical Tutorial at  http://flask.pocoo.org/docs/0.10/patterns/fileuploads/
# see links for further understanding
###################################################

from os import environ
import flask
from flask import Flask, Response, request, render_template, redirect, url_for
from flaskext.mysql import MySQL
import flask_login

# for image uploading
import os
import base64

mysql = MySQL()
app = Flask(__name__)
app.secret_key = 'super secret string'  # Change this!

# These will need to be changed according to your creditionals
app.config['MYSQL_DATABASE_USER'] = environ.get('MYSQL_DATABASE_USER')
app.config['MYSQL_DATABASE_PASSWORD'] = environ.get('MYSQL_DATABASE_PASSWORD')
app.config['MYSQL_DATABASE_DB'] = environ.get('MYSQL_DATABASE_DB')
app.config['MYSQL_DATABASE_HOST'] = environ.get('MYSQL_DATABASE_HOST')
mysql.init_app(app)

# begin code used for login
login_manager = flask_login.LoginManager()
login_manager.init_app(app)

conn = mysql.connect()
cursor = conn.cursor()
cursor.execute("SELECT email from Users")
users = cursor.fetchall()


def getUserList():
    cursor = conn.cursor()
    cursor.execute("SELECT email from Users")
    return cursor.fetchall()


class User(flask_login.UserMixin):
    # def get_id(self):
    # 	return (self.id)
    pass


@login_manager.user_loader
def user_loader(email):
    users = getUserList()
    if not(email) or email not in str(users):
        return
    user = User()
    user.id = email
    user.email = email
    return user


@login_manager.request_loader
def request_loader(request):
    users = getUserList()
    email = request.form.get('email')
    if not(email) or email not in str(users):
        return
    user = User()
    user.id = email
    user.email = email
    cursor = mysql.connect().cursor()
    cursor.execute(
        "SELECT password FROM Users WHERE email = '{0}'".format(email))
    data = cursor.fetchall()
    pwd = str(data[0][0])
    user.is_authenticated = request.form['password'] == pwd
    return user


'''
A new page looks like this:
@app.route('new_page_name')
def new_page_function():
	return new_page_html
'''


@app.route('/login', methods=['GET', 'POST'])
def login():
    if flask.request.method == 'GET':
        return '''
			   	<form action='login' method='POST'>
					<input type='text' name='email' id='email' placeholder='email'></input>
					<input type='password' name='password' id='password' placeholder='password'></input>
					<input type='submit' name='submit' value='Submit'></input>
			   	</form></br>
		   		<a href='/'>Home</a>
			   '''
    # The request method is POST (page is recieving data)
    email = flask.request.form['email']
    cursor = conn.cursor()
    # check if email is registered
    if cursor.execute("SELECT password FROM Users WHERE email = '{0}'".format(email)):
        data = cursor.fetchall()
        pwd = str(data[0][0])
        if flask.request.form['password'] == pwd:
            user = User()
            user.id = email
            user.email = email
            flask_login.login_user(user)  # okay login in user
            # protected is a function defined in this file
            return flask.redirect(flask.url_for('protected'))

    # information did not match
    return "<a href='/login'>Try again</a>\
			</br><a href='/register'>or make an account</a>"


@app.route('/logout')
def logout():
    flask_login.logout_user()
    return render_template('hello.html', message='Logged out')


@login_manager.unauthorized_handler
def unauthorized_handler():
    return render_template('unauth.html')

# you can specify specific methods (GET/POST) in function header instead of inside the functions as seen earlier


@app.route("/register", methods=['GET'])
def register():
    return render_template('register.html', supress='True')


@app.route("/register", methods=['POST'])
def register_user():
    try:
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        email = request.form.get('email')
        password = request.form.get('password')
        gender = request.form.get('gender')
        date_of_birth = request.form.get('date_of_birth')
        hometown = request.form.get('hometown')
    except:
        # this prints to shell, end users will not see this (all print statements go to shell)
        print("couldn't find all tokens")
        return flask.redirect(flask.url_for('register'))
    cursor = conn.cursor()
    test = isEmailUnique(email)
    if test:
        print(cursor.execute("INSERT INTO Users (first_name, last_name, email, password, gender, date_of_birth, hometown, contribution_score) VALUES ('{0}', '{1}', '{2}', '{3}', '{4}', '{5}', '{6}', 0)".format(
            first_name, last_name, email, password, gender, date_of_birth, hometown)))
        conn.commit()
        # log user in
        user = User()
        user.id = email
        user.email = email
        flask_login.login_user(user)
        return render_template('hello.html', email=email, message='Account Created!')
    else:
        print("email not unique")
        return flask.redirect(flask.url_for('register'))


def getUsersPhotos(uid):
    cursor = conn.cursor()
    cursor.execute(
        "SELECT imgdata, picture_id, caption FROM Photos WHERE user_id = '{0}'".format(uid))
    # NOTE return a list of tuples, [(imgdata, pid, caption), ...]
    return cursor.fetchall()


def getUserIdFromEmail(email):
    cursor = conn.cursor()
    cursor.execute(
        "SELECT user_id FROM Users WHERE email = '{0}'".format(email))
    return cursor.fetchone()[0]


def isEmailUnique(email):
    # use this to check if a email has already been registered
    cursor = conn.cursor()
    if cursor.execute("SELECT email FROM Users WHERE email = '{0}'".format(email)):
        # this means there are greater than zero entries with that email
        return False
    else:
        return True
# end login code


@app.route('/profile')
@flask_login.login_required
def protected():
    return render_template('hello.html', email=flask_login.current_user.email, message="Here's your profile")


# FRIENDS FUNCTIONALITY CODE HERE
@app.route('/friends')
@flask_login.login_required
def friends():
    uid = getUserIdFromEmail(flask_login.current_user.email)
    friends_list = getFriends(uid)
    return render_template('friends.html', friends_list=friends_list)


@app.route("/search_users", methods=['GET'])
def search_users():
    return render_template('search_users.html')


@app.route("/search_users", methods=['POST'])
def search():
    first_name = request.form.get('first_name')
    users = searchOtherUsersByFirstName(first_name)

    return render_template('search_users.html', users=users)

# Takes a user's id and first name as args


@app.route("/add_friend")
def add_friend():
    args = request.args
    addressee_id = args.get('addressee_id')
    addressee_first_name = args.get('addressee_first_name')
    requestor_id = getUserIdFromEmail(flask_login.current_user.email)

    cursor = conn.cursor()
    print(cursor.execute("INSERT INTO Friendships (requestor_id, addressee_id) VALUES ({0}, {1})".format(
        requestor_id, addressee_id)))
    conn.commit()

    return render_template('friends.html', message=addressee_first_name + ' added as Friend!')


def getFriends(uid):
    cursor = conn.cursor()
    cursor.execute(
        "SELECT user_id, first_name, last_name, gender, hometown, email FROM Users WHERE user_id IN (SELECT addressee_id FROM Friendships WHERE requestor_id = {0});".format(uid))
    return cursor.fetchall()


def searchOtherUsersByFirstName(first_name):
    curr_user_id = getUserIdFromEmail(flask_login.current_user.email)
    cursor = conn.cursor()
    cursor.execute("SELECT user_id, first_name, last_name, gender, hometown FROM Users WHERE first_name LIKE '{0}%' AND user_id <> {1}".format(
        first_name, curr_user_id))
    return cursor.fetchall()

# End Friends code


# begin photo uploading code
# photos uploaded using base64 encoding so they can be directly embeded in HTML
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


@app.route('/upload', methods=['GET', 'POST'])
@flask_login.login_required
def upload_file():
    if request.method == 'POST':
        uid = getUserIdFromEmail(flask_login.current_user.email)
        imgfile = request.files['photo']
        caption = request.form.get('caption')
        photo_data = imgfile.read()
        cursor = conn.cursor()
        cursor.execute(
            '''INSERT INTO Photos (imgdata, user_id, caption) VALUES (%s, %s, %s )''', (photo_data, uid, caption))
        conn.commit()
        return render_template('hello.html', email=flask_login.current_user.email, message='Photo uploaded!', photos=getUsersPhotos(uid), base64=base64)
    # The method is GET so we return a  HTML form to upload the a photo.
    else:
        return render_template('upload.html')
# end photo uploading code


# default page
@app.route("/", methods=['GET'])
def hello():
    return render_template('hello.html', message='Welecome to Photoshare')


if __name__ == "__main__":
    # this is invoked when in the shell  you run
    # $ python app.py
    app.run(port=5000, debug=True)

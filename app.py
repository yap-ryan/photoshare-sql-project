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
from tkinter import S
import flask
from flask import Flask, Response, request, render_template, redirect, url_for
from flaskext.mysql import MySQL
import flask_login

# for image uploading
import os
import base64

from pymysql import NULL

mysql = MySQL()
app = Flask(__name__)
app.secret_key = 'super secret string'  # Change this!

#These will need to be changed according to your creditionals
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'MySQLPass420!'
app.config['MYSQL_DATABASE_DB'] = 'photoshareTEST7'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'

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
            return flask.redirect(flask.url_for('protected'))   # protected is a function defined in this file

    # information did not match
    return "<a href='/login'>Try again</a>\
			</br><a href='/register'>or make an account</a>"




@login_manager.unauthorized_handler
def unauthorized_handler():
    return render_template('unauth.html')

# you can specify specific methods (GET/POST) in function header instead of inside the functions as seen earlier

# begin top 10 contributors code 

def topContributors() : 

    cursor = conn.cursor()
    cursor.execute(
        '''
        Select U.user_id, U.first_name, U.last_name, contribution_score
        From Users U
        GROUP BY U.user_id
        ORDER BY contribution_score DESC   
        ''')
    topContributorTable = cursor.fetchall(); 

    num_top_contributors = 0
    topTopContributorTable = []

    for contributor in topContributorTable : 
        
        if num_top_contributors < 10: 
            topTopContributorTable.append(contributor)
            num_top_contributors = num_top_contributors + 1
        else : 
            break; 

    return topTopContributorTable


# end top 10 contributors code 

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
        return render_template('hello.html', top_contributors = topContributors() , email=email, message='Account Created!')
    else:
        print("email not unique")
        return flask.redirect(flask.url_for('register'))

@app.route('/logout')
def logout():
    flask_login.logout_user()
    return render_template('hello.html', top_contributors = topContributors(), message='Logged out')

def getUsersPhotos(uid):
    cursor = conn.cursor()
    cursor.execute(
        "SELECT data, photo_id, caption FROM Photos WHERE user_id = '{0}'".format(uid))
    # NOTE return a list of tuples, [(imgdata, pid, caption), ...]
    return cursor.fetchall()


def getAlbumsPhotos(albumid):
	cursor = conn.cursor()
	cursor.execute("SELECT photo_id, data, caption FROM Photos WHERE album_id = '{0}'".format(albumid))
	return cursor.fetchall() #NOTE return a list of tuples, [(imgdata, pid, caption), ...]


def getContributionScore(uid):
    cursor = conn.cursor()
    cursor.execute("SELECT contribution_score FROM Users WHERE user_id = '{0}'".format(uid))
    return cursor.fetchone()

def incContributionScore(uid):
    cursor = conn.cursor()
    cursor.execute("UPDATE Users SET contribution_score = contribution_score + 1 WHERE user_id ='{0}'".format(uid))
    conn.commit()

def getUsersAlbums(uid):
	cursor = conn.cursor()
	cursor.execute("SELECT album_name FROM Albums WHERE user_id = '{0}'".format(uid))
	return cursor.fetchall()  #return list of all of the albums owned by that user 

def deleteAlbum(album_name):
	cursor = conn.cursor()
	cursor.execute("DELETE FROM Albums WHERE album_name = '{0}'".format(album_name))
	conn.commit()

def deletePhoto(photo_id):
	cursor = conn.cursor()
	cursor.execute("DELETE FROM Photos WHERE photo_id = '{0}'".format(photo_id))
	conn.commit()

def getPhotosComments(photo_id):
	cursor = conn.cursor()
	cursor.execute("SELECT date, text FROM Comments WHERE photo_id = '{0}' ORDER BY date".format(photo_id))
	return cursor.fetchall()  #return list of all of the user ids 

def getAllUserIds():
	cursor = conn.cursor()
	cursor.execute("SELECT user_id FROM Users")
	return cursor.fetchall()  #return list of all of the user ids 


def getUserIdFromEmail(email):
    cursor = conn.cursor()
    cursor.execute(
        "SELECT user_id FROM Users WHERE email = '{0}'".format(email))
    return cursor.fetchone()[0]


def getAlbumIdFromName(name):
	cursor = conn.cursor()
	cursor.execute("SELECT album_id FROM Albums WHERE album_name = '{0}'".format(name))
	return cursor.fetchone()[0]

def getUserIdFromPhotoID(photo_id):
	cursor = conn.cursor()
	cursor.execute("SELECT user_id FROM Photos WHERE photo_id = '{0}'".format(photo_id))
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
    return render_template('hello.html', top_contributors = topContributors(), email=flask_login.current_user.email, message="Here's your profile")


# FRIENDS FUNCTIONALITY CODE HERE
@app.route('/friends')
@flask_login.login_required
def friends():
    uid = getUserIdFromEmail(flask_login.current_user.email)
    friends_list = getFriends(uid)
    return render_template('friends.html', friends_list=friends_list)


@app.route("/search_users", methods=['GET'])
def search_users():
    uid = getUserIdFromEmail(flask_login.current_user.email)
    recommendation_ls = getFriendRecommendations(uid)

    return render_template('search_users.html', rec_ls=recommendation_ls)


@app.route("/search_users", methods=['POST'])
def search():
    first_name = request.form.get('first_name')
    users = searchOtherUsersByFirstName(first_name)
    
    return render_template('search_users.html', users=users)


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
    
    friends_list = getFriends(requestor_id)
    
    return render_template('friends.html', message=addressee_first_name + ' added as Friend!', friends_list=friends_list)


def getFriends(uid):
    cursor = conn.cursor()
    cursor.execute(
        "SELECT user_id, first_name, last_name, gender, hometown, email FROM Users WHERE user_id IN (SELECT addressee_id FROM Friendships WHERE requestor_id = {0});".format(uid))
    return cursor.fetchall()

# Takes uid and returns a list of friends-of-friends(mutuals) who are not the current user or user's friends
def getFriendRecommendations(uid):
    cursor = conn.cursor()
    cursor.execute(
        '''
        SELECT rec.mutual_id, f.first_name, f.last_name, COUNT(rec.mutual_id) AS shared_friends
        FROM Users f, 
            (SELECT f1.addressee_id AS friend_id, f2.addressee_id AS mutual_id
            FROM (SELECT * FROM Friendships WHERE requestor_id = {0}) AS f1, Friendships f2
            WHERE f2.requestor_id = f1.addressee_id 
                AND f2.addressee_id NOT IN (SELECT addressee_id FROM Friendships WHERE requestor_id = {0})
                AND f2.addressee_id <> {0}) AS rec
        WHERE rec.mutual_id = f.user_id
        GROUP BY rec.mutual_id
        ORDER BY shared_friends DESC;
        '''.format(uid))
    
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

        uid = getUserIdFromEmail(flask_login.current_user.email)
        album_list = getUsersAlbums(uid)

        if request.method == 'POST':
            imgfile = request.files['photo']
            caption = request.form.get('caption')
            tag_string = request.form.get('tags')
            photo_data =imgfile.read()
            cursor = conn.cursor()
            albumname = request.form.get('selectalbum')
            
            # Insert photo
            album_id = getAlbumIdFromName(albumname)		
            cursor.execute('''INSERT INTO Photos (data, caption, album_id, user_id) VALUES (%s, %s ,%s, %s)''', (photo_data, caption, album_id, uid))
            photo_id = cursor.lastrowid
            incContributionScore(uid)
  
            # Insert tags
            tags = tag_string.split()
            for i in range(0,len(tags)):
                cursor.execute('''INSERT INTO Tags (text, photo_id) VALUES (%s, %s)''', (tags[i], photo_id))

            conn.commit()
            return render_template('hello.html', name=flask_login.current_user.email, message='Photo uploaded!', photos=getUsersPhotos(uid), base64=base64)
        #The method is GET so we return a  HTML form to upload the a photo.
        else: 
            return render_template('upload.html', album_list = album_list)
#end photo uploading code

#begin create new album code 

ALLOWED_EXTENSIONS2 = set(['png', 'jpg', 'jpeg', 'gif'])
def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS2

@app.route('/createalbum', methods=['GET', 'POST'])
@flask_login.login_required
def create_new_album():
    uid = getUserIdFromEmail(flask_login.current_user.email)

    if request.method == 'POST':
        imgfile = request.files['photo']
        caption = request.form.get('caption')
        tag_string = request.form.get('tags')
        photo_data =imgfile.read()
        cursor = conn.cursor()
        createdalbum = request.form.get('albumname')
        date = request.form.get('date')

        # Insert album
        cursor.execute('''INSERT INTO Albums (album_name, creation_date, user_id) VALUES (%s, %s, %s )''', (createdalbum, date, uid))
        album_id = getAlbumIdFromName(createdalbum)	

        # Insert photo
        cursor.execute('''INSERT INTO Photos (data, caption, album_id, user_id) VALUES (%s, %s ,%s, %s)''', (photo_data, caption, album_id, uid))
        photo_id = cursor.lastrowid
        incContributionScore(uid) 

        # Insert tags
        tags = tag_string.split()
        for i in range(0,len(tags)):
            cursor.execute('''INSERT INTO Tags (text, photo_id) VALUES (%s, %s)''', (tags[i], photo_id))

        conn.commit()
        return render_template('hello.html', name=flask_login.current_user.email, message='Photo uploaded!', photos=getUsersPhotos(uid), base64=base64)
	
	#The method is GET so we return a  HTML form to upload the a photo.
    else:
	    return render_template('createalbum.html')

#end create new album code 

#begin view all albums code 

@app.route('/viewallalbums', methods=['GET', 'POST'])
def viewAllAlbums(): 
    user_id_list = getAllUserIds()
    album_list_of_all_users = []
    
    for x in user_id_list :
        album_one_user = getUsersAlbums(x[0])
        for y in album_one_user : 
            album_list_of_all_users.append(y)
    
    return render_template('viewallalbums.html', album_list = album_list_of_all_users, user_list = user_id_list)


#end view all albums code 



# begin view one album for unregistered user code 

@app.route('/viewonealbumunreg', methods=['GET', 'POST'])
def viewonealbumunreg(): 
    args = request.args 
    album_name = args.get('album_name')
    album_id = getAlbumIdFromName(album_name)
    photos = getAlbumsPhotos(album_id)
    
    
    return render_template('viewonealbumunreg.html',  photos=photos, base64=base64)

# end view one album for unregistered user code 




#begin view user albums code 

@app.route('/viewuseralbums', methods=['GET', 'POST'])
@flask_login.login_required
def viewUserAlbums(): 
	uid = getUserIdFromEmail(flask_login.current_user.id)
	albums = getUsersAlbums(uid)

	return render_template('viewuseralbums.html', album_list = albums)


#end view user albums code 



# begin view one album for registered user code 

@app.route('/viewonealbumuser', methods=['GET', 'POST'])
def viewonealbumuser(): 

	args = request.args 

	album_name = args.get('album_name')
	
	album_id = getAlbumIdFromName(album_name)

	photos = getAlbumsPhotos(album_id)
	return render_template('viewonealbumuser.html', album_id = album_id, photos=photos, base64=base64)

# end view one album for registered user code 


# Begin Tags code

# NOTE: Hyperlinks result in GET requests!
@app.route('/search_tags', methods=['GET','POST'])
def search_tags():
    if request.method == 'POST':
        
        tag_string = request.form.get('tags')
            
        photo_data = getPhotosByTag(tag_string) # Format: [(photo_id, data, caption), ...]
            
        return render_template('tagview.html', tags = tag_string, photos = photo_data, base64=base64)
    else:
        # ARGS USED IF USING TAG HYPERLINK
        if request.args:
            args = request.args
            tag_string = args.get('tag')
            photo_data = getPhotosByTag(tag_string) # Format: [(photo_id, data, caption), ...]

            return render_template('tagview.html', tags = tag_string, photos=photo_data, base64=base64)
		
        return render_template('tagview.html')
    
@app.route('/search_user_tags', methods=['GET','POST'])
@flask_login.login_required
def search_my_tags():
    if request.method == 'POST':
                
        uid = getUserIdFromEmail(flask_login.current_user.id)
        tag_string = request.form.get('tags')
        photo_data = getUserPhotosByTag(tag_string,uid) # Format: [(photo_id, data, caption), ...]
        
        return render_template('registered_tagview.html', tags = tag_string, photos = photo_data, base64=base64)
    else:
        return render_template('registered_tagview.html')

# Accepts string of tags
# EXAMPLE INPUTS: "friends", "friends boston"
# NOTE: This is a Conjunctive search
def getPhotosByTag(tags):
    tag_list = tags.split()
    num_tags = len(tag_list)
    
    if num_tags == 0:
        return       

    query = '''
            SELECT p.photo_id, p.data, p.caption
            FROM Photos p,
                (SELECT DISTINCT t.photo_id 
                FROM Tags t
                WHERE t.text = \"%s\"
            ''' % tag_list[0]
            
    for i in range(1, num_tags):
        query += " AND t.photo_id IN (SELECT t{0}.photo_id FROM Tags t{0} WHERE t{0}.text = \"{1}\")".format(str(i), tag_list[i])
    
    query += ") AS tg WHERE p.photo_id = tg.photo_id;"
    
    cursor = conn.cursor()
    cursor.execute(query)
    
    return cursor.fetchall()   

def getUserPhotosByTag(tags, uid):
    tag_list = tags.split()
    num_tags = len(tag_list)
    
    if num_tags == 0:
        return       

    query = '''
            SELECT p.photo_id, p.data, p.caption
            FROM Photos p,
                (SELECT DISTINCT t.photo_id 
                FROM Tags t
                WHERE t.text = \"%s\"
            ''' % tag_list[0]
            
    for i in range(1, num_tags):
        query += " AND t.photo_id IN (SELECT t{0}.photo_id FROM Tags t{0} WHERE t{0}.text = \"{1}\")".format(str(i), tag_list[i])
    
    query += ") AS tg WHERE p.photo_id = tg.photo_id AND p.user_id = {0};".format(uid)
    
    print(query)
    cursor = conn.cursor()
    cursor.execute(query)
    
    return cursor.fetchall()

def getTagsOfPhoto(photo_id):
    
    query = '''
            SELECT t.text
            FROM Tags t
            WHERE t.photo_id = %s;
            ''' % photo_id
            
    cursor = conn.cursor()
    cursor.execute(query)
    
    return cursor.fetchall()

def getPopularTags(count):
    
    query = '''
			SELECT t.text, COUNT(*) AS Cnt
			FROM Tags t
			GROUP BY t.text
			ORDER BY Cnt DESC
			LIMIT %s;
    		''' % count
    
    cursor = conn.cursor()
    cursor.execute(query)
    return cursor.fetchall()  

  
# End Tags code

@app.route('/search_on_comment', methods=['GET','POST'])
def search_on_comment():
    if request.method == 'POST':
        text = request.form.get('comment')
        user_data = searchOnComment(text)
        return render_template('search_on_comments.html', user_data=user_data, text=text)
    else:
        return render_template('search_on_comments.html')


def searchOnComment(text):
    query = '''
            SELECT u.user_id, u.first_name, u.last_name, cmts.cnt
            FROM Users u, (SELECT c.user_id, COUNT(*) as cnt
                FROM Comments c
                WHERE c.text = '%s'
                GROUP BY c.user_id) AS cmts
            WHERE cmts.user_id = u.user_id
            ORDER BY cmts.cnt DESC;
            ''' % text
    
    cursor = conn.cursor()
    cursor.execute(query)
    return cursor.fetchall()


# Start Recommendations (You May Also Like Feature) Code

@app.route('/you_may_like', methods=['GET'])
@flask_login.login_required
def you_may_like():
	uid = getUserIdFromEmail(flask_login.current_user.id)
	user_tags = getUserPopularTags(uid,5)
	tag_string = ""
 
	# Build tag_string
	for tag in user_tags:
		tag_string += tag[0] + " "
  
	print(tag_string)

	photo_count = getOtherPhotosByTag(uid, tag_string) # Format: [(photo_id, data, caption, cntMatches), ...]
 
	photo_data = []
	count_map = {5: [], 4: [], 3: [], 2: [], 1: []}
 
	# Populate count_map
	for p in photo_count:
		match_count = p[3]
		p_id = p[0]
		num_tags = len(getTagsOfPhoto(p_id))
		
		count_map[match_count].append((p_id, p[1], p[2], num_tags))
  
	# test = []
	for cnt in count_map:
		count_map[cnt].sort(key = lambda x: x[3])
		for photo in count_map[cnt]:
			# test.append((photo[0],photo[3]))
			photo_data.append(photo)

	# print(test)
		
	return render_template('you_may_like.html', tags = tag_string, photos = photo_data, base64=base64)

def getUserPopularTags(uid, count):
    
    query = '''
			SELECT t.text, COUNT(*) AS Cnt
			FROM Tags t, Photos p
			WHERE t.photo_id = p.photo_id AND p.user_id = %s 
			GROUP BY t.text
			ORDER BY Cnt DESC
			LIMIT %s;
    		''' % (uid, count)
    
    cursor = conn.cursor()
    cursor.execute(query)
    return cursor.fetchall()

# NOTE: This is a Disjunctive tag search 
def getOtherPhotosByTag(uid, tags):
    tag_list = tags.split()
    num_tags = len(tag_list)
    
    if num_tags == 0:
        return       

    query = '''
            SELECT m.photo_id, p.data, p.caption, m.cntMatches
			FROM Photos p,
				(SELECT t.photo_id, COUNT(t.photo_id) as cntMatches
				FROM Tags t
				WHERE t.text = \"%s\"
            ''' % tag_list[0]
            
    for i in range(1, num_tags):
        query += " OR t.text = \"%s\"" % tag_list[i]
    
    query += '''
    		GROUP BY t.photo_id) AS m
			WHERE p.photo_id = m.photo_id AND p.user_id <> %s
			ORDER BY cntMatches DESC;
    		''' % uid
    
    cursor = conn.cursor()
    cursor.execute(query)
    
    return cursor.fetchall()   

# End Recommendations Code


# begin comments code 


@app.route('/insertcomment', methods=['GET', 'POST'])
def insertcomment(): 
    args = request.args
    photo_id = args.get('photo_id')
    date = request.form.get('date')
    text = request.form.get('comment')

    if (flask_login.current_user.is_authenticated) : 
        
        uid = getUserIdFromEmail(flask_login.current_user.id)
        user_id_from_photo = getUserIdFromPhotoID(photo_id)

        if not (user_id_from_photo == uid) : 

            cursor = conn.cursor()
            cursor.execute("INSERT INTO Comments ( text, date, user_id, photo_id) VALUES (%s, %s, %s, %s);", (text, date, uid, photo_id))
            conn.commit() 
            incContributionScore(uid)
            return (''), 204 
        else: 
            return (''), 204 
    else: 
        cursor = conn.cursor()
        cursor.execute("INSERT INTO Comments ( text, date, user_id, photo_id) VALUES (%s, %s,%s, %s);", (text, date,None, photo_id))
        conn.commit() 
        return (''), 204 

# end comments code 



# Start 'Like Photo' code

# Adds a like to a photo
@app.route('/add_like', methods=['GET', 'POST'])
def add_like():
    args = request.args
    photo_id = args.get('photo_id')

    uid = getUserIdFromEmail(flask_login.current_user.id)
    
    query = "INSERT INTO Likes (user_id, photo_id) VALUES (%s, %s);" % (uid, photo_id)
    
    cursor = conn.cursor()
    cursor.execute(query)
    conn.commit()  
    
    return (''), 204

# Function to return string of all user emails who liked a photo
def getLikeList(photo_id):
    query = '''
			SELECT u.email
			FROM Users u, Likes l
			WHERE l.photo_id = %s AND u.user_id = l.user_id;
   			''' % photo_id
    
    cursor = conn.cursor()
    cursor.execute(query)
    
    user_emails = ""
    
    for tup in cursor.fetchall() :
        user_emails += tup[0] + " "
    
    return user_emails

# Function to get number of likes on a photo
def getLikes(photo_id):
    query = '''
    		SELECT COUNT(l.user_id)
			FROM Likes l
			WHERE l.photo_id = %s;
      		''' % photo_id
    
    cursor = conn.cursor()
    cursor.execute(query)
    res = cursor.fetchone()
	
    return res[0]

# End 'Like Photo' code


@app.context_processor
def utility_processor():
    uid = None
    if flask_login.current_user.is_authenticated:
        uid = getUserIdFromEmail(flask_login.current_user.id)
    
    return {'getTagsOfPhoto': getTagsOfPhoto, 'insertcomment' : insertcomment, 'getPhotosComments': getPhotosComments, 'getPopularTags': getPopularTags, 'getLikes': getLikes, 'getLikeList': getLikeList, 'isAuth': flask_login.current_user.is_authenticated, 'uid': uid}

#begin delete album code 

@app.route('/deletealbum', methods=['GET', 'POST'])
@flask_login.login_required
def deletealbum(): 

    args = request.args 

    album_name = args.get('album_name')
   
    deleteAlbum(album_name)

    uid = getUserIdFromEmail(flask_login.current_user.id)
    albums = getUsersAlbums(uid)

    return render_template('viewuseralbums.html', album_list = albums) 


# end delete album code 




#begin delete photo code 

@app.route('/deletephoto', methods=['GET', 'POST'])
@flask_login.login_required
def deletephoto(): 

    args = request.args 

    photo_id = args.get('photo_id')
    album_id = args.get('album_id')
   
    deletePhoto(photo_id)


    photos = getAlbumsPhotos(album_id)
    return render_template('viewonealbumuser.html',  photos=photos, base64=base64)


# end delete photo code 





#default page
@app.route("/", methods=['GET'])
def hello():
	return render_template('hello.html', top_contributors = topContributors(), message='Welcome to Photoshare')


if __name__ == "__main__":
	#this is invoked when in the shell  you run
	#$ python app.py
	app.run(port=5000, debug=True)


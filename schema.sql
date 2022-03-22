CREATE DATABASE IF NOT EXISTS photoshareTEST2;
USE photoshareTEST2;

CREATE TABLE Users(
    user_id INTEGER AUTO_INCREMENT, 
    password CHAR(10), 
    gender CHAR(1), 
    first_name VARCHAR(20), 
    last_name VARCHAR(20), 
    email VARCHAR(20) UNIQUE,
	date_of_birth DATE, 
	hometown VARCHAR(20), 
	contribution_score INTEGER, 

	PRIMARY KEY (user_id), 

	CHECK (contribution_score >= 0), 
	CHECK (gender='f' OR gender='m' OR gender='n')
); 

CREATE TABLE Friendships(
    requestor_id INTEGER NOT NULL,
    addressee_id INTEGER NOT NULL,

	PRIMARY KEY (requestor_id, addressee_id),
	FOREIGN KEY (requestor_id) 
		REFERENCES Users(user_id),
	FOREIGN KEY (addressee_id) 
		REFERENCES Users(user_id),
	CHECK (requestor_id <> addressee_id)
);


CREATE TABLE Albums(
    album_id INTEGER AUTO_INCREMENT, 
    album_name VARCHAR(20) UNIQUE, 
    creation_date DATE, 

    user_id INTEGER NOT NULL, 

    PRIMARY KEY (album_id),
    FOREIGN KEY (user_id) 
		REFERENCES Users(user_id)
); 



CREATE TABLE Photos(
    photo_id INTEGER AUTO_INCREMENT,
    data longblob NOT NULL,
    caption VARCHAR(255),
    album_id INTEGER NOT NULL, 
    user_id INTEGER NOT NULL,


    PRIMARY KEY (photo_id),
    FOREIGN KEY (album_id)
        REFERENCES Albums(album_id)
        ON DELETE CASCADE
    FOREIGN KEY (user_id)
        REFERENCES Users(user_id)
);

CREATE TABLE Likes(
	user_id INTEGER NOT NULL,
	photo_id INTEGER NOT NULL,

	PRIMARY KEY (user_id, photo_id),
	FOREIGN KEY (user_id) 
		REFERENCES Users(user_id),
	FOREIGN KEY (photo_id) 
		REFERENCES Photos(photo_id)
);

CREATE TABLE Comments(
    comment_id INTEGER AUTO_INCREMENT,
    text VARCHAR(255),
    date DATE,
    user_id INTEGER,
    photo_id INTEGER NOT NULL,

    PRIMARY KEY (comment_id),
    FOREIGN KEY (user_id) 
		REFERENCES Users(user_id),
    FOREIGN KEY (photo_id) 
		REFERENCES Photos(photo_id)
		ON DELETE CASCADE
);


CREATE TABLE Tags(
    text VARCHAR(100), 
    photo_id INTEGER NOT NULL, 

    PRIMARY KEY (text, photo_id), 
    FOREIGN KEY (photo_id) 
		REFERENCES Photos(photo_id) 
		ON DELETE CASCADE
); 

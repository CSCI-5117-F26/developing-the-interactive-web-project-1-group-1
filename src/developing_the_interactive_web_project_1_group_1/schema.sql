/*
References for Database schema       

                                                                                                                                   POSTS
CREATE TABLE POST
Post ID (uuid) or SEIAL
user_id
Photo_id
title
Description
Lost and found location
Tag (drop down location)
Posted date/time (Time stamp)

CREATE TABLE User
User ID (uuid)
auth_id

CREATE TABLE image_store
photo_id
image_name
image_data

CREATE TABLE Comment

User ID
Comment Text
Created Date and Time

*/
CRETE TABLE User(
    user_id SERIAL PRIMARY,
    auth_id VARCHAR(255) UNIQUE NOT NULL,
    display_name VARCHAR(255) NOT NULL, /* For auto generate hidden name we mentioned*/
    created_at TIMESTAMP DEFAULT NOW() 
    /*seeing a common theme online for timestamp on user at creation,
     not 100% sure why yet but why not add it I guess */
)


CREATE TABLE images(
photo_id SEIAL PRIMARY KEY,
image_name VARCHAR(255) NOT NULL,
image_data bytea NOT NULL
);

CREATE TABLE tag_location(
    location_id SERIAL PRIMARY KEY
    building_name VARCHAR(100) NOT NULL UNIQUE
)
CREATE TABLE tag_item(
    item_id SERIAL PRIMARY KEY
    item_name VARCHAR(100) NOT NULL UNIQUE
)

CREATE TABLE Post (
    Post_id SERIAL PRIMARY KEY,
    /*Undecided about if posts will be a weak relationship to Users ON DELETE CASCADE*/
    user_id SERIAL NOT NULL REFERENCES users(user_id),
    photo_id SERIAL NOT NULL REFERENCES images(photo_id),
    title TEXT NOT NULL,
    tag_location NOT NULL,
    tag_item NOT NULL,

    description TEXT
    timestamp TIMESTAMP DEFAULT NOW()

)

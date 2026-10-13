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

CREATE TABLE Post (
    Post_id SERIAL
    user_id SERIAL
    photo_id SERIAL

)

CREATE TABLE image_store(
photo_id INT AUTO_INCREMENT PRIMARY KEY,
image_name VARCHAR(255) NOT NULL,
image_data LONGBLOB NOT NULL
);
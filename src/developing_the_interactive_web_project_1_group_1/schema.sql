CREATE TABLE user(
    user_id SERIAL PRIMARY,
    auth_id VARCHAR(255) UNIQUE NOT NULL,
    display_name VARCHAR(255) NOT NULL, /* For auto generate hidden name we mentioned,at server side*/
    created_at TIMESTAMP DEFAULT NOW() 
    /*seeing a common theme online for timestamp on user at creation,
     not 100% sure why yet but why not add it I guess */
)

/*NOTE you have to check the file type in server before sending...
File type validation on server side, */
CREATE TABLE images(
photo_id SEIAL PRIMARY KEY,
image_name VARCHAR(255) NOT NULL,
image_data BYTEA NOT NULL
);

/*Created these tables so we can add building and item types for selection as we need */
CREATE TABLE tag_building(
    location_id SERIAL PRIMARY KEY
    building_name VARCHAR(100) NOT NULL UNIQUE
)
CREATE TABLE tag_itemtype(
    item_id SERIAL PRIMARY KEY
    item_name VARCHAR(100) NOT NULL UNIQUE
)

CREATE TABLE post (
    post_id SERIAL PRIMARY KEY,
    /*Undecided about if posts will be a weak relationship to Users ON DELETE CASCADE*/
    user_id SERIAL NOT NULL REFERENCES users(user_id),
    photo_id SERIAL NOT NULL REFERENCES images(photo_id),
    title TEXT NOT NULL,
    tag_location SERIAL NOT NULL REFERENCES tag_building(location_id),
    tag_item SERIAL NOT NULL REFERENCES tag_itemtype(item_id),

    description TEXT
    timestamp TIMESTAMP DEFAULT NOW()

)
/*Make comments a weak relationship to post, since will delete if posts is delete*/
CREATE TABLE comments(
    comment_id SERIAL PRIMARY KEY
    post_id SERIAL NOT NULL REFERENCES posts(post_id) ON DELETE CASCADE,
    /*With userid can get display name from it, and ties ownership to them*/
    user_id SERIAL NOT NULL REFERENCES users(user_id),
    comment_info TEXT NOT NULL
    timestamp TIMESTAMP DEFAULT NOW()
)
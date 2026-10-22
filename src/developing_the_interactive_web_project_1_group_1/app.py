import os
import random
import mimetypes
from datetime import datetime, timezone
from functools import wraps
from authlib.integrations.flask_client import OAuth, OAuthError
from dotenv import load_dotenv
from flask import Flask, request, render_template, redirect, session, url_for, abort, Response, flash
from developing_the_interactive_web_project_1_group_1 import database

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ["FLASK_SECRET_KEY"]

# 10MB limit
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024

database.setup()

oauth = OAuth(app)
oauth.register(
    "auth0",
    client_id=os.environ["AUTH0_CLIENT_ID"],
    client_secret=os.environ["AUTH0_CLIENT_SECRET"],
    client_kwargs={"scope": "openid profile email"},
    server_metadata_url=f'https://{os.environ["AUTH0_DOMAIN"]}/.well-known/openid-configuration',
)

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session or database.get_user(session['user_id']) is None:
            session.clear()
            if request.method == 'GET':
                session['next_url'] = request.path
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated


def get_own_post(post_id):
    post = database.get_post(post_id)
    if post is None:
        abort(404)
    if post['user_id'] != session['user_id']:
        abort(403)
    return post

def post_form_error(title, location_id, item_id, photo, buildings, item_types, photo_required):
    has_photo = photo is not None and photo.filename != ''
    if not title:
        return "Please enter a title."
    if location_id not in [b['location_id'] for b in buildings]:
        return "Please choose a building."
    if item_id not in [t['item_id'] for t in item_types]:
        return "Please choose an item type."
    if photo_required and not has_photo:
        return "Please add a photo."
    if has_photo and not photo.mimetype.startswith('image/'):
        return "The photo must be an image file."
    return None

@app.template_filter('time_ago')
def time_ago(when):
    seconds = (datetime.now(timezone.utc) - when).total_seconds()
    if seconds < 60:
        return "just now"
    if seconds < 3600:
        return f"{int(seconds // 60)} min ago"
    if seconds < 86400:
        return f"{int(seconds // 3600)} hr ago"
    return f"{int(seconds // 86400)} days ago"

@app.route('/')
def index():
    search = request.args.get('q', '').strip()
    location_id = request.args.get('building', type=int)
    item_id = request.args.get('item_type', type=int)
    limit = request.args.get('limit', 20, type=int)
    limit = max(1, min(limit, 200))

    # Get one extra post to know if there are more to load
    posts = database.get_posts(search, location_id, item_id, limit + 1)
    has_more = len(posts) > limit

    return render_template('index.html', posts=posts[:limit], has_more=has_more, limit=limit,
                           buildings=database.get_buildings(), item_types=database.get_item_types())

@app.route('/login')
def login():
    return oauth.auth0.authorize_redirect(
        redirect_uri=url_for('callback', _external=True)
    )

@app.route('/callback')
def callback():
    # Handle Auth0 if login declines and return to home
    try:
        token = oauth.auth0.authorize_access_token()
    except OAuthError as e:
        session.pop('next_url', None)
        if e.error == 'access_denied':
            flash("Login cancelled.")
        else:
            flash("Something went wrong while logging in.")
        return redirect(url_for('index'))
    userinfo = token['userinfo']
    email = userinfo.get('email', '').lower()
    if not email.endswith('@umn.edu') or not userinfo.get('email_verified'):
        if email.endswith('@umn.edu'):
            message = "Please verify your UMN email, then log in again."
        elif userinfo['sub'].startswith('google-oauth2|'):
            # Auth0 ids start with how they logged in
            message = "Please sign in with your UMN Google account."
        else:
            message = "Please sign in with an @umn.edu email account."
        session.clear()
        flash(message)
        return auth0_logout(url_for('index', _external=True))

    display_name = f"user{random.randint(1000, 9999)}"
    user = database.get_or_create_user(userinfo['sub'], display_name)

    session['user'] = token
    session['user_id'] = user['user_id']
    session['display_name'] = user['display_name']
    # Return to page user attempted to log in from
    next_url = session.pop('next_url', url_for('index'))
    return redirect(next_url)

def auth0_logout(return_to):
    return redirect(
        f'https://{os.environ["AUTH0_DOMAIN"]}/v2/logout'
        f'?returnTo={return_to}&client_id={os.environ["AUTH0_CLIENT_ID"]}'
    )

@app.route('/logout')
def logout():
    session.clear()
    return auth0_logout(url_for('index', _external=True))

@app.route('/create-post', methods=['GET', 'POST'])
@login_required
def create_post():
    buildings = database.get_buildings()
    item_types = database.get_item_types()

    if request.method == 'GET':
        return render_template('create_post.html', buildings=buildings, item_types=item_types)

    title = request.form.get('title', '').strip()
    description = request.form.get('details', '').strip()
    location_id = request.form.get('building', type=int)
    item_id = request.form.get('item_type', type=int)
    photo = request.files.get('photo')

    error = post_form_error(title, location_id, item_id, photo, buildings, item_types, photo_required=True)
    if error:
        return render_template('create_post.html', buildings=buildings, item_types=item_types,
                               error=error, form=request.form), 400

    database.create_post(session['user_id'], title, description, location_id, item_id,
                         photo.filename, photo.read())
    return redirect(url_for('my_posts'))

@app.route('/my-posts')
@login_required
def my_posts():
    posts = database.get_posts_for_user(session['user_id'])
    return render_template('my_posts.html', posts=posts)

@app.route('/account')
@login_required
def account():
    return render_template('account.html')

@app.route('/posts/<int:post_id>', methods=['GET'])
#no login required
def view_post(post_id):
    post = database.get_post(post_id)
    if post is None:
        abort(404)

    user = database.get_user(post['user_id'])
    is_users_post = session.get('user_id', None) == post['user_id']  

    buildings = database.get_buildings()
    # find the building that matches the tag_location number associated with our post
    building = next((i for i in buildings if i.get('location_id') == post['tag_location']), None)

    item_types = database.get_item_types()
    # find the item_type that matches the tag_item number associated with our post
    item_type = next((i for i in item_types if i.get('item_id') == post['tag_item']), None)

    return render_template('view_post.html', post=post, user=user, building=building, 
                           item_type=item_type, is_users_post=is_users_post)

@app.route('/posts/<int:post_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_post(post_id):
    post = get_own_post(post_id)
    buildings = database.get_buildings()
    item_types = database.get_item_types()

    if request.method == 'GET':
        form = {'title': post['title'], 'details': post['description'] or '',
                'building': str(post['tag_location']), 'item_type': str(post['tag_item'])}
        error = None
        if request.args.get('too_big'):
            error = "File is too large. Upload size limit is 10MB"
        return render_template('create_post.html', post=post, buildings=buildings,
                               item_types=item_types, form=form, error=error)

    title = request.form.get('title', '').strip()
    description = request.form.get('details', '').strip()
    location_id = request.form.get('building', type=int)
    item_id = request.form.get('item_type', type=int)
    photo = request.files.get('photo')

    error = post_form_error(title, location_id, item_id, photo, buildings, item_types, photo_required=False)
    if error:
        return render_template('create_post.html', post=post, buildings=buildings, item_types=item_types,
                               error=error, form=request.form), 400

    if photo is not None and photo.filename != '':
        database.update_post(post_id, session['user_id'], title, description, location_id, item_id,
                             photo.filename, photo.read())
    else:
        database.update_post(post_id, session['user_id'], title, description, location_id, item_id)
    return redirect(url_for('my_posts'))

@app.route('/posts/<int:post_id>/delete', methods=['POST'])
@login_required
def delete_post(post_id):
    get_own_post(post_id)
    database.delete_post(post_id, session['user_id'])
    return redirect(url_for('my_posts'))

@app.route('/images/<int:photo_id>')
def image(photo_id):
    img = database.get_image(photo_id)
    if img is None:
        abort(404)
    mimetype = mimetypes.guess_type(img['image_name'])[0] or 'application/octet-stream'
    return Response(img['image_data'], mimetype=mimetype)

@app.errorhandler(413)
def too_large(e):
    if request.endpoint == 'edit_post':
        return redirect(url_for('edit_post', post_id=request.view_args['post_id'], too_big=1))
    return render_template('create_post.html', buildings=database.get_buildings(),
                           item_types=database.get_item_types(),
                           error="File is too large. Upload size limit is 10MB"), 413

if __name__ == '__main__':
    app.run() 

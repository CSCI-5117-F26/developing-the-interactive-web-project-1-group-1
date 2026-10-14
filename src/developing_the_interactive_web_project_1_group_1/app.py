import os
import random
import mimetypes
from datetime import datetime, timezone
from functools import wraps
from authlib.integrations.flask_client import OAuth
from dotenv import load_dotenv
from flask import Flask, request, render_template, redirect, session, url_for, abort, Response
import database

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ["FLASK_SECRET_KEY"]

app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024
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

        if 'user_id' not in session:
            return redirect(url_for('login'))
        
        if database.get_user(session['user_id']) is None:
            session.clear()
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated



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
    token = oauth.auth0.authorize_access_token()
    display_name = f"user{random.randint(1000, 9999)}"
    user = database.get_or_create_user(token['userinfo']['sub'], display_name)

    session['user'] = token
    session['user_id'] = user['user_id']
    session['display_name'] = user['display_name']
    return redirect(url_for('index'))

@app.route('/logout')
def logout():
    session.clear()
    return_to = url_for('index', _external=True)
    return redirect(
        f'https://{os.environ["AUTH0_DOMAIN"]}/v2/logout'
        f'?returnTo={return_to}&client_id={os.environ["AUTH0_CLIENT_ID"]}'
    )

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

    error = None
    if not title:
        error = "Please enter a title."
    elif location_id not in [b['location_id'] for b in buildings]:
        error = "Please choose a building."
    elif item_id not in [t['item_id'] for t in item_types]:
        error = "Please choose an item type."
    elif photo is None or photo.filename == '':
        error = "Please add a photo."
    elif not photo.mimetype.startswith('image/'):
        error = "The photo must be an image file."

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

@app.route('/posts/<int:post_id>/delete', methods=['POST'])
@login_required
def delete_post(post_id):
    post = database.get_post(post_id)
    if post is None:
        abort(404)

    if post['user_id'] != session['user_id']:
        abort(403)
    database.delete_post(post_id)
    return redirect(url_for('my_posts'))

@app.route('/images/<int:photo_id>')
def image(photo_id):
    img = database.get_image(photo_id)
    if img is None:
        abort(404)
    mimetype = mimetypes.guess_type(img['image_name'])[0] or 'application/octet-stream'
    return Response(img['image_data'], mimetype=mimetype)

if __name__ == '__main__':
    app.run() 

import os
from functools import wraps
from authlib.integrations.flask_client import OAuth
from dotenv import load_dotenv
from flask import Flask, request, render_template, redirect, session, url_for

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ["FLASK_SECRET_KEY"]

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
        if 'user' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated



@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login')
def login():
    return oauth.auth0.authorize_redirect(
        redirect_uri=url_for('callback', _external=True)
    )

@app.route('/callback')
def callback():
    token = oauth.auth0.authorize_access_token()
    session['user'] = token
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
    return render_template('create_post.html')

@app.route('/my-posts')
@login_required
def my_posts():
    # demo data until we have a database
    posts = [
        {'title': 'Black AirPods', 'building': 'Keller Hall', 'comments': 2},
        {'title': 'Blue Owala', 'building': 'Rec Center', 'comments': 0},
        {'title': 'Umbrella', 'building': 'Anderson Hall', 'comments': 1},
    ]
    return render_template('my_posts.html', posts=posts)

if __name__ == '__main__':
    app.run() 

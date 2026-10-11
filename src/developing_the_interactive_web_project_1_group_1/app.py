from flask import Flask, request, render_template
from clip_search import embed_text, sim_score
import numpy as np

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/create-post', methods=['GET', 'POST'])
def create_post():
    return render_template('create_post.html')

@app.route('/my-posts')
def my_posts():
    # demo data until we have a database
    posts = [
        {'title': 'Black AirPods', 'building': 'Keller Hall', 'comments': 2},
        {'title': 'Blue Owala', 'building': 'Rec Center', 'comments': 0},
        {'title': 'Umbrella', 'building': 'Anderson Hall', 'comments': 1},
    ]
    return render_template('my_posts.html', posts=posts)

@app.route('/search', methods=['GET'])
def search():
    query = request.args.get("q","").strip()
    # query_vec = embed_text(query)
    # # get query, emded text, get images and cal sim score, return higest sim score
    # # GET IMAGE VECTORS FROM DB
    # #imgs = filter from db
    # imgs = None
    # img_matrix = np.stack([np.frombuffer(img.clip_embedding, dtype=np.float32) for img in imgs])
    # scores = img_matrix @ query_vec
    # idxs = np.argsort(-scores)[:10]
    # render_template("some template", query = query , 
    # results = [{"image" : imgs[i]} for i in idxs])
    return render_template("index.html", query = query , results = query )
if __name__ == '__main__':
    app.run() 

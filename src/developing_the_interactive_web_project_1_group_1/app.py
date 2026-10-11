from flask import Flask, request, render_template, url_for, Response
from clip_search import embed_text, embed_img
import upload_item
import numpy as np
from io import BytesIO
# import some db package and run setup

app = Flask(__name__)

upload_item.setup()
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

@app.route('/test', methods=['GET', 'POST'])
def test_upload():
    if request.method == "GET":
        return render_template("index.html")
    photo = request.files.get("photo")
    
    img_bytes = photo.read()
    emds = embed_img(BytesIO(img_bytes))
    emds_bytes = emds.astype(np.float32).tobytes()
    upload_item.insert(img_bytes,emds_bytes)
    return render_template('index.html')

@app.route('/get_img/<int:img_id>', methods=['GET', 'POST'])
def get_img(img_id):
    row = upload_item.get_one(img_id)
    return Response(row["image_data"], mimetype="image/jpeg")

@app.route('/search', methods=['GET'])
def search():
    query = request.args.get("q","").strip()
    query_vec = embed_text(query)
    # get query, emded text, get images and cal sim score, return higest sim score
    # GET IMAGE VECTORS FROM DB
    #imgs = filter from db
    imgs = upload_item.get_all()
    img_matrix = np.stack([np.frombuffer(img["embedding"], dtype=np.float32) for img in imgs])
    scores = img_matrix @ query_vec
    idxs = np.argsort(-scores)[:10]
    results = [
        {
            "img_url": url_for("get_img", img_id = imgs[i]["id"]),
            "title": "Test Title",
            "location": "Keller",
            "item_type": ["item Type 1", "item Type 2"],
            "posted_ago": "3"
        } for i in idxs
    ]
    return render_template("index.html", query = query , results = results)
if __name__ == '__main__':
    app.run() 

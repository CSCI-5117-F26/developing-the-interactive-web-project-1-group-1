from flask import Flask, request, render_template

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

if __name__ == '__main__':
    app.run() 

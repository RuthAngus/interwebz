# http://127.0.0.1:5000/
from load_tex import load_tex
from flask import Flask, request
from flask import render_template
app = Flask(__name__)


# Render the front page
@app.route('/')
def index():
    return render_template('index.html')


# Parse form entry to load_tex and return result
@app.route('/load-tex', methods=["POST"])
def scrape():
    arxiv_number = str(request.form["arxiv_number"])
    text = load_tex(arxiv_number)
    return "{0}".format(text)

if __name__ == '__main__':
    app.run(debug=True)

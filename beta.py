# http://127.0.0.1:5000/
from load_tables import load_tables
from arxiv import get_article
from flask import Flask, request
from flask import render_template
app = Flask(__name__)


# Render the front page
@app.route('/')
def index():
    return render_template('index.html')


# Parse form entry to load_tex and return result
@app.route('/find-tables', methods=["POST"])
def scrape():
    arxiv_number = str(request.form["arxiv_number"])
    get_article(arxiv_number)
    data_list, header_list, unit_list = load_tables(arxiv_number)
    return render_template('data.html', ntables=len(data_list),
                           header="{0}".format(header_list[0]),
                           data="{0}".format(data_list[0]))

# # Display table and select variables
# @app.route('/table/<int:tnumber>', methods=["POST"])
# def select_variables(tnumber):
#     data_list, header_list, unit_list = load_tables(arxiv_number)
#     return render_template('table.html', header="{0}".format(header_list[0]),
#                            data="{0}".format(data_list[0]))


if __name__ == '__main__':
    app.run(debug=True)

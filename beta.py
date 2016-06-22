# http://127.0.0.1:5000/
import numpy as np
from load_tables import load_tables
from html_tooltips import make_html_fig
from arxiv import get_article
from flask import Flask, request
from flask import render_template
from astropy.table import Table
from flask import session
import pandas as pd

app = Flask(__name__)

secret_key = np.genfromtxt("secret_key.txt", dtype=str)
app.secret_key = "23B9FD8E7EAE4964FD4F15F857DB7"

# Render the front page
@app.route('/')
def index():
    return render_template('index.html')


# Parse form entry to load_tex and return result
@app.route('/find-tables', methods=["POST"])
def scrape():
    arxiv_number = str(request.form["arxiv_number"])
    # g.an = arxiv_number
    with open("number.txt", "w") as f:
        f.write("{0}".format(arxiv_number))
    get_article("{0}".format(arxiv_number))
    data_list, header_list, unit_list = load_tables(arxiv_number)
    return render_template('data.html', ntables=len(data_list),
                           header="{0}".format(header_list[0]),
                           data="{0}".format(data_list[0]))

# Display table and select variables
@app.route('/table/<int:tnumber>', methods=["GET", "POST"])
def select_variables(tnumber):
    with open("number.txt", "r") as f:  # FIXME: use g instead
        arxiv_number = f.read()
    data_list, header_list, unit_list = load_tables(arxiv_number)
    headers, data = header_list[tnumber], data_list[tnumber]  # select table
    headers = [i.replace("$", "") for i in headers]  # clean up data
    headers = [i.replace("\\", "") for i in headers]  # clean up data
    ncolumns, nrows = len(headers), len(data)
    mydict = dict(zip(headers, data))  # make a dictionary of data
    table = pd.DataFrame(mydict)  # make a pandas dataframe of data
    session["tab"] = table.to_json()  # convert pandas df to json
    return render_template('table.html', header_list=headers, data=data,
                           ncolumns=ncolumns, nrows=nrows)

# test inserting figure
@app.route('/figure')
def make_figure():
    t = session.get("tab")  # load the json of the data
    data = pd.read_json(t).as_matrix()
    table = make_html_fig(t)
    return "{}".format(table)
    return render_template('html_tooltips.html')


if __name__ == '__main__':
    app.run(debug=True)

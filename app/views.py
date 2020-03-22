from app import app
from flask import render_template
import os

@app.route('/')
def home():
   return "{}, {}, {}".format(os.environ['MTAA_DB_ADDR'], os.environ['MTAA_DB_PORT'], os.environ['MTAA_DB_DB'])

@app.route('/template')
def template():
    return render_template('home.html')

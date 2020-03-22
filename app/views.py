from app import app
from flask import render_template

@app.route('/')
def home():
   return "<b>Mareek :-)</b>"

@app.route('/template')
def template():
    return render_template('home.html')

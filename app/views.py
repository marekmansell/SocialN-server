from app import app
from flask import render_template
import psycopg2
import os

conn = psycopg2.connect(
		database=os.environ['MTAA_DB_DB'],
		user=os.environ['MTAA_DB_USER'],
		password=os.environ['MTAA_DB_PASS'],
		host=os.environ['MTAA_DB_ADDR'],
		port=os.environ['MTAA_DB_PORT']
	)

@app.route('/')
def home():
	cur = conn.cursor()

	cur.execute("SELECT id, name, address, salary  from COMPANY")
	rows = cur.fetchall()


	html = [" ".join([str(x).strip() for x in row]) for row in rows]

	return "<br>".join(html)

@app.route('/add/')
def add():
	cur = conn.cursor()
	cur.execute("INSERT INTO COMPANY (ID,NAME,AGE,ADDRESS,SALARY) \
	      VALUES (9, 'Allen', 25, 'Texas', 15000.00 )")

	conn.commit()

@app.route('/template')
def template():
    return render_template('home.html')

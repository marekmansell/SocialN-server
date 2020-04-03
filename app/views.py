import os

import psycopg2
from flask import render_template, request, g
from flask_restful import Resource

from app import app, api


def get_db():
    if 'db' not in g:
        g.db = psycopg2.connect(
            database=os.environ['MTAA_DB_DB'],
            user=os.environ['MTAA_DB_USER'],
            password=os.environ['MTAA_DB_PASS'],
            host=os.environ['MTAA_DB_ADDR'],
            port=os.environ['MTAA_DB_PORT']
        )

    return g.db


def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()


@app.route('/')
def index():
    db = get_db()
    cur = db.cursor()

    cur.execute("SELECT id, name, address, salary  from COMPANY")
    rows = cur.fetchall()

    html = [" ".join([str(x).strip() for x in row]) for row in rows]

    return "<br>.".join(html)


@app.route('/add/')
def add():
    db = get_db()
    cur = db.cursor()
    cur.execute("INSERT INTO COMPANY (ID,NAME,AGE,ADDRESS,SALARY) "
                "VALUES (10, 'Marek', 21, 'Texas', 15000.00 )")

    db.commit()
    return "OK"


@app.route('/init/')
def init_db():
    db = get_db()

    with db.cursor() as cursor:
        schema_file_path = os.path.join("app", "postgresql", "schema.sql")

        with open(schema_file_path, "r") as file:
            cursor.execute(file.read())

    return "OK"


@api.resource('/v1/hello')
class HelloWorld(Resource):
    def get(self):
        print(request.authorization)
        # print(dict(request.headers))
        # print(request.form)
        return {'hello': 'world'}

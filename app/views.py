import os
import random
import string

import psycopg2
from flask import render_template, request, g, make_response, jsonify
from flask_restful import Resource, abort

from app import app, api

TOKEN_CHARACTERS = string.ascii_lowercase + string.ascii_uppercase + string.digits


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


def get_token_from_request(request):
    return request.headers['Authorization'].split(' ')[1]


def authenticate_token(request):
    response = {}

    if not request.headers.get('Authorization', None):
        response['authenticated'] = 'false'
        response['errors'] = {'authorization_header': ['missing']}
        response['hint'] = "Please check the authorization header of the request."
        abort_with_response(response, 401)

    if len(request.headers['Authorization'].split(' ')) != 2:
        response['authenticated'] = 'false'
        response['errors'] = {'authorization_header': ['wrong']}
        response['hint'] = "Please check the authorization header of the request."
        abort_with_response(response, 401)

    token = request.headers['Authorization'].split(' ')[1]

    token_sql_result = sql_query("users", ['username'], where=f"token = '{token}'")

    if not token_sql_result or not token_sql_result[0][0]:
        response['authenticated'] = 'false'
        response['errors'] = {'token': ['wrong']}
        response['hint'] = "Please check token or contact the administrator."
        abort_with_response(response, 401)

    return


@app.errorhandler(404)
def page_not_found(e):
    return f"The page you have requested was not found -> {request.url}\n", 404


@app.route('/')
def index():
    db = get_db()

    try:
        with db.cursor() as cursor:
            cursor.execute("SELECT * from users")
            users_rows = cursor.fetchall()

            cursor.execute("SELECT COLUMN_NAME FROM information_schema.COLUMNS WHERE TABLE_NAME = 'users';")
            users_row_names = cursor.fetchall()

            cursor.execute("SELECT * from posts")
            posts_rows = cursor.fetchall()

            cursor.execute("SELECT COLUMN_NAME FROM information_schema.COLUMNS WHERE TABLE_NAME = 'posts';")
            posts_row_names = cursor.fetchall()

    except Exception as e:
        db.rollback()
        return f"Error: {e}"

    return render_template("index.html", users_rows=users_rows, users_row_names=users_row_names, posts_rows=posts_rows,
                           posts_row_names=posts_row_names)


@app.route('/add/user/')
def add():
    db = get_db()

    try:
        with db.cursor() as cursor:
            cursor.execute("INSERT INTO users (username, formatted_name, password, mail, date_of_birth) "
                           "VALUES ('marekmansell3', 'Marek Mansell', 'pass123', 'm@m.sk', '2020-03-02')")
            db.commit()
    except Exception as e:
        db.rollback()
        return f"Error: {e}"

    return "OK"


@app.route('/add/post/')
def add_post():
    db = get_db()

    try:
        with db.cursor() as cursor:
            cursor.execute(f"INSERT INTO posts (user_id, publish_time, content) VALUES"
                           f"( (SELECT id from users WHERE username='marekmansell'), '2020-12-12', 'ABCD...' );")
            db.commit()
    except Exception as e:
        db.rollback()
        return f"Error: {e}"

    return "OK"


@app.route('/init/')
def init_db():
    db = get_db()

    try:
        with db.cursor() as cursor:
            schema_file_path = os.path.join("app", "postgresql", "schema.sql")

            with open(schema_file_path, "r") as file:
                cursor.execute(file.read())
                db.commit()

    except Exception as e:
        return f"Error: {e}"

    return "OK"


@app.route('/init/test/')
def test_init():
    db = get_db()

    try:
        with db.cursor() as cursor:
            schema_file_path = os.path.join("app", "postgresql", "schema.sql")

            with open(schema_file_path, "r") as file:
                cursor.execute(file.read())
                db.commit()

            cursor.execute("INSERT INTO users (username, formatted_name, password, mail, date_of_birth) "
                           "VALUES ('exampleUser', 'Mr. Example', 'Nbu123sr', 'example@example.com', '2020-03-02')")

            cursor.execute("INSERT INTO users (username, formatted_name, password, mail, date_of_birth) "
                           "VALUES ('superUser', 'Someone naughty', 'naughty', 'example@example.com', '2020-03-02')")
            db.commit()


    except Exception as e:
        return f"Error: {e}"

    return "OK"

@api.resource('/v1/hello')
class HelloWorld(Resource):
    def get(self):
        response = {}

        if not request.authorization:
            response['authenticated'] = 'false'
            response['errors'] = {'basic_auth': ['none']}
            response['hint'] = "Include a HTTP basic auth with your user name and password for authentication."
            abort_with_response(response, 401)

        if not request.authorization.get('username', None):
            response['authenticated'] = 'false'
            response['errors'] = {'user': ['none']}
            response['hint'] = "Please enter a user for the HTTP basic authentication."
            abort_with_response(response, 401)

        if not request.authorization.get('password', None):
            response['authenticated'] = 'false'
            response['errors'] = {'password': ['none']}
            response['hint'] = "Please enter a password for the HTTP basic authentication."
            abort_with_response(response, 401)

        user_password_result = sql_query("users", ["password"],
                                         where=f"username = '{request.authorization['username']}'")

        if not user_password_result:
            response['authenticated'] = 'false'
            response['errors'] = {'user': ['wrong']}
            response['hint'] = "Please check the username for any typos or contact the administrator."
            abort_with_response(response, 401)

        if user_password_result[0][0] != request.authorization['password']:
            response['authenticated'] = 'false'
            response['errors'] = {'password': ['wrong']}
            response['hint'] = "Please check the password for any typos or contact the administrator."
            abort_with_response(response, 401)

        user_token_result = sql_query("users", ["token"], where=f"username = '{request.authorization['username']}'")

        user_token = user_token_result[0][0]
        if not user_token_result[0][0]:
            user_token = ''.join(random.choices(TOKEN_CHARACTERS, k=40))
            sql_update("users", f"token = '{user_token}'", f"username = '{request.authorization['username']}'")

        response['authenticated'] = 'true'
        response['access_token'] = user_token
        return response, 200


@api.resource('/v1/users')
class GetAllUsers(Resource):
    def get(self):
        response = {}

        authenticate_token(request)
        check_content_type(request)

        column_names = ['id', 'username', 'formatted_name', 'bio', 'photo', 'web', 'mail', 'date_of_birth']
        users_json = sql_query("users", column_names, json=True)
        response['users'] = users_json

        return response, 200


@api.resource('/v1/users/<requested_user>')
class GetUser(Resource):
    def get(self, requested_user):
        response = {}

        authenticate_token(request)
        check_content_type(request)

        column_names = ['id', 'username', 'formatted_name', 'bio', 'photo', 'web', 'mail', 'date_of_birth']
        users_json = sql_query("users", column_names, json=True, where=f"username = '{requested_user}'")
        response['users'] = users_json

        return response, 200

    def patch(self, requested_user):
        response = {}

        authenticate_token(request)
        check_content_type(request)

        user_sql_result = sql_query('users', ['username'], where=f"token = '{get_token_from_request(request)}'")
        if user_sql_result[0][0] != requested_user:
            response['authenticated'] = True
            response['error'] = {'method': 'forbidden'}
            response['hint'] = "The user you are signed in to does not have priviledges to change other user's profiles"
            return response, 403

        # sql_update('user', _set="s" )
        # To DO - update with SQL

        allowed_keys = ['formatted_name', 'password', 'bio', 'photo', 'web', 'mail', 'date_of_birth']

        sql_update_query = []

        for key in request.json['user']:
            if key not in allowed_keys:
                response['authenticated'] = True
                response['error'] = {f"{key}": 'forbidden'}
                response['hint'] = f"The key {key} is not allowed to change!"
                return response, 403
            else:
                sql_update_query.append(f"{key} = '{request.json['user'][key]}'")

        sql_update_query = ", ".join(sql_update_query)

        sql_update("users", sql_update_query, f"username = '{requested_user}'")

        column_names = ['id', 'username', 'formatted_name', 'bio', 'photo', 'web', 'mail', 'date_of_birth']
        users_json = sql_query("users", column_names, json=True, where=f"username = '{requested_user}'")
        response['users'] = users_json

        return response, 200


@api.resource('/v1/post/')
class Posts(Resource):
    def get(self):
        response = {}

        authenticate_token(request)
        check_content_type(request)

        column_names = ['posts.id', "users.username", 'users.formatted_name', 'posts.publish_time', 'posts.photo',
                        'posts.content', 'posts.last_edit_time']
        users_json = sql_query("posts", column_names, json=True, join="JOIN users ON (users.id = posts.user_id)")
        response['posts'] = users_json

        return response, 200

    def post(self):
        response = {}

        authenticate_token(request)
        check_content_type(request)

        if not request.get_json(silent=True) or not request.json.get('post'):
            response['error'] = {"post": "missing"}
            response['hint'] = "Please enter the parameters you want to update."
            return response, 422

        allowed_keys = ['photo', 'content']

        sql_update_query = {}

        for key in request.json['post']:
            if key not in allowed_keys:
                response['authenticated'] = True
                response['error'] = {f"{key}": 'forbidden'}
                response['hint'] = f"The key {key} is not allowed to change!"
                return response, 403
            else:
                sql_update_query[key] = request.json['post'][key]

        if not request.json.get('post').get('content'):
            response['authenticated'] = True
            response['error'] = {f"{'content'}": 'none'}
            response['hint'] = f"The content of the post is missing, try adding some!"
            return response, 422


        sub_sql_values = {}
        sub_sql_values['user_id'] = f"(SELECT id from users WHERE token='{get_token_from_request(request)}')"
        sql_update_query['publish_time'] = "2019-10-10"

        result_id = sql_insert("posts", sql_update_query, sub_sql_values)

        column_names = ['posts.id', "users.username", 'users.formatted_name', 'posts.publish_time', 'posts.photo',
                        'posts.content', 'posts.last_edit_time']
        users_json = sql_query("posts", column_names, json=True, where=f"posts.id = '{result_id}'",
                               join="JOIN users ON (users.id = posts.user_id)")
        response['posts'] = users_json

        return response, 200


@api.resource('/v1/post/<requested_post_id>')
class Post(Resource):
    def get(self, requested_post_id):
        response = {}

        authenticate_token(request)
        check_content_type(request)

        column_names = ['posts.id', "users.username", 'users.formatted_name', 'posts.publish_time', 'posts.photo',
                        'posts.content', 'posts.last_edit_time']
        users_json = sql_query("posts", column_names, json=True, where=f"id = '{requested_post_id}'",
                               join="JOIN users ON (users.id = posts.user_id)")
        response['posts'] = users_json

        return response, 200

    def delete(self, requested_post_id):
        response = {}

        authenticate_token(request)
        check_content_type(request)

        posts_sql = sql_query("posts", ['id'], json=True, where=f"id = '{requested_post_id}'")
        if not posts_sql:
            response['errors'] = {'post': 'does_not_exist'}
            response['hint'] = "No post with the given post ID found, check the post ID"
            return response, 422

        requested_id_sql = sql_query('users', ['id'], where=f"token = '{get_token_from_request(request)}'")
        requested_id_request = sql_query('posts', ['user_id'], where=f"id = '{requested_post_id}'")
        if requested_id_sql[0][0] != requested_id_request[0][0]:
            response['authenticated'] = True
            response['error'] = {'method': 'forbidden'}
            response['hint'] = "The user you are signed in to does not have privileges to change other user's profiles"
            return response, 403

        sql_delete("posts", where=f"id = '{requested_post_id}'")
        return response, 204

    def patch(self, requested_post_id):
        response = {}

        authenticate_token(request)
        check_content_type(request)

        requested_id_sql = sql_query('users', ['id'], where=f"token = '{get_token_from_request(request)}'")
        requested_id_request = sql_query('posts', ['user_id'], where=f"id = '{requested_post_id}'")
        if requested_id_sql[0][0] != requested_id_request[0][0]:
            response['authenticated'] = True
            response['error'] = {'method': 'forbidden'}
            response['hint'] = "The user you are signed in to does not have privileges to change other user's profiles"
            return response, 403


        allowed_keys = ['photo', 'content']

        sql_update_query = []

        if not request.get_json(silent=True) or not request.json.get('post'):
            response['error'] = {"post": "missing"}
            response['hint'] = "Please enter the parameters you want to update."
            return response, 403

        for key in request.json['post']:
            if key not in allowed_keys:
                response['authenticated'] = True
                response['error'] = {f"{key}": 'forbidden'}
                response['hint'] = f"The key {key} is not allowed to change!"
                return response, 403
            else:
                sql_update_query.append(f"{key} = '{request.json['post'][key]}'")

        sql_update_query = ", ".join(sql_update_query)

        sql_update("posts", sql_update_query, where=f"id = '{requested_post_id}'")

        column_names = ['posts.id', "users.username", 'users.formatted_name', 'posts.publish_time', 'posts.photo',
                        'posts.content', 'posts.last_edit_time']
        users_json = sql_query("posts", column_names, json=True, where=f"posts.id = '{requested_post_id}'",
                               join="JOIN users ON (users.id = posts.user_id)")
        response['posts'] = users_json

        return response, 200


# Returns the multi-line result of a sql query as a JSON dictionary
def sql_query_result_to_json(query_result, column_names):
    users_json_list = []
    for row in query_result:
        row_json = {}
        for i, column in enumerate(column_names):
            if row[i]:
                row_json[column] = str(row[i])
            else:
                row_json[column] = row[i]

        users_json_list.append(row_json)
    return users_json_list


# Returns the SQL query results
def sql_query(table_name, column_names, where="", json=False, join=""):
    response = {}

    db = get_db()

    if where:
        where_query = f"WHERE {where}"
    else:
        where_query = ""

    try:
        with db.cursor() as cursor:

            cursor.execute(f"SELECT {', '.join(column_names)} FROM {table_name} {join} {where_query};")
            users_raw = cursor.fetchall()
            if json:
                return sql_query_result_to_json(users_raw, column_names)
            else:
                return users_raw

    except Exception as e:
        db.rollback()
        response['errors'] = {'server_error': 'unknown'}
        response['hint'] = "Please wait or contact the administrator."
        response['error'] = str(e)
        print(e)
        print(f"SELECT {', '.join(column_names)} FROM {table_name} {join} {where_query};")
        abort_with_response(response, 500)


def abort_with_response(response, status_code):
    abort(make_response(jsonify(response), status_code))


def sql_update(table_name, _set, where):
    response = {}

    db = get_db()

    try:
        with db.cursor() as cursor:

            cursor.execute(f"UPDATE {table_name} SET {_set} WHERE {where};")
            db.commit()

    except Exception as e:
        db.rollback()
        response['errors'] = {'server_error': 'unknown'}
        response['hint'] = "Please wait or contact the administrator."
        response['error'] = str(e)
        abort_with_response(response, 500)


def sql_delete(table_name, where):
    response = {}

    db = get_db()

    try:
        with db.cursor() as cursor:

            cursor.execute(f"DELETE FROM {table_name} WHERE {where};")
            db.commit()

    except Exception as e:
        db.rollback()
        response['errors'] = {'server_error': 'unknown'}
        response['hint'] = "Please wait or contact the administrator."
        response['error'] = str(e)
        print(f"DELETE FROM {table_name} WHERE {where};")
        abort_with_response(response, 500)


def sql_insert(table_name, keyed_values, sub_sql_values):

    db = get_db()

    try:
        with db.cursor() as cursor:

            sql_columns = []
            sql_values = []

            for key in sub_sql_values:
                sql_columns.append(key)
                sql_values.append(sub_sql_values[key])

            for key in keyed_values:
                sql_columns.append(key)
                sql_values.append(f"'{keyed_values[key]}'")

            sql_columns_str = ", ".join(sql_columns)
            sql_values_str = ", ".join(sql_values)

            cursor.execute(f"INSERT INTO {table_name} ({sql_columns_str}) VALUES "
                           f"( {sql_values_str} ) RETURNING id;")
            result_id = cursor.fetchone()[0]
            db.commit()

            return result_id

    except Exception as e:
        response = {}
        db.rollback()
        response['errors'] = {'server_error': 'unknown'}
        response['hint'] = "Please wait or contact the administrator."
        response['error'] = str(e)
        print(f"INSERT INTO {table_name} ({sql_columns_str}) VALUES "
              f"( {sql_values_str} );")
        abort_with_response(response, 500)


def check_content_type(request):
    if not request.content_type or not request.content_type.startswith('application/json'):
        response = {'error': {'media-type': 'unsupported'}, 'hint': "Use 'application/json' media type"}
        abort_with_response(response, 445)


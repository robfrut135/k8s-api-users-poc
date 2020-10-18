import hashlib
import json
import os

import MySQLdb
from flask import Flask, request, jsonify
from redis import Redis

app = Flask(__name__)
redis_client = Redis(
    host=os.environ.get("REDIS_HOST", "redis"),
    port=os.environ.get("REDIS_PORT", 6379),
)
db = MySQLdb.connect(
    os.environ.get("MYSQL_HOST", "mysql"),
    os.environ.get("MYSQL_USER", "root"),
    os.environ.get("MYSQL_ROOT_PASSWORD", "password")
)
cursor = db.cursor()


def __get_user_key(userid):
    return "users:" + hashlib.sha224(bytes(userid, encoding="UTF-8")).hexdigest()


@app.route("/users/health")
def health():
    return jsonify({"message": "Ok"}), 200


@app.route("/users/init")
def init():
    app.logger.info("Begin")
    app.logger.info("Delete database if exists")
    cursor.execute("DROP DATABASE IF EXISTS users_db")
    app.logger.info("Create database")
    cursor.execute("CREATE DATABASE users_db")
    app.logger.info("Create users tables")
    cursor.execute("USE users_db")
    sql = """CREATE TABLE users (
         user_id int,
         user_name char(30)
     )"""
    cursor.execute(sql)
    db.commit()
    app.logger.info("End")
    return jsonify({"message": "Database ready"}), 200


@app.route("/users", methods=["POST"])
def add_user():
    app.logger.info("Begin")
    data = request.get_json()
    user_id = data.get('user_id', None)
    user_name = data.get('user_name', None)
    app.logger.info("Check user data")
    if user_id and user_name:
        app.logger.info("Insert user")
        cursor.execute("INSERT INTO users_db.users (user_id, user_name) VALUES (%s,%s)", (user_id, user_name))
        db.commit()
        resp = jsonify({"message": "Created"}), 201
    else:
        app.logger.info("User not valid")
        resp = jsonify({"message": "BadRequest"}), 400
    app.logger.info("End")
    return resp


@app.route("/users/<user_id>", methods=["GET"])
def get_user(user_id):
    app.logger.info("Begin")
    userid = str(user_id)
    app.logger.info("Generate Redis key")
    key = __get_user_key(userid)
    app.logger.info(f"Check if user was cached, key={key}")
    if redis_client.exists(key):
        app.logger.info("Return cached user")
        resp = jsonify(json.loads(redis_client.get(key))), 200
    else:
        app.logger.info("Search in database")
        cursor.execute(f"SELECT user_id, user_name FROM users_db.users WHERE user_id={userid}")
        data = cursor.fetchone()
        if data:
            user = {"user_id": data[0], "user_name": data[1]}
            app.logger.info("Found user in database, update cache")
            redis_client.set(key, json.dumps(user))
            redis_client.expire(key, 36)
            app.logger.info("Return user from database")
            resp = jsonify(user), 200
        else:
            app.logger.info("User not found")
            resp = jsonify({"message": "NotFound"}), 404
    app.logger.info("End")
    return resp


@app.route("/users/<user_id>", methods=["DELETE"])
def del_user(user_id):
    app.logger.info("Begin")
    userid = str(user_id)
    key = __get_user_key(userid)
    app.logger.info("Select user from db")
    cursor.execute(f"SELECT user_name FROM users_db.users WHERE user_id={userid}")
    data = cursor.fetchone()
    if data:
        app.logger.info("Delete user in database")
        cursor.execute(f"DELETE FROM users_db.users WHERE user_id={userid}")
        app.logger.info("Delete user in cache")
        redis_client.delete(key)
        resp = jsonify({"message": "Deleted"}), 204
    else:
        app.logger.info("User not found")
        resp = jsonify({"message": "NotFound"}), 404
    app.logger.info("End")
    return resp


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)

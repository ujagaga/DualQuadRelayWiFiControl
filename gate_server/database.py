import sys
import sqlite3
import os

current_path = os.path.dirname(os.path.realpath(__file__))
db_path = os.path.join(current_path, "database.db")


def init_database():
    if not os.path.isfile(db_path):
        # Database does not exist. Create one
        db = sqlite3.connect(db_path)

        sql = "create table users (email TEXT NOT NULL UNIQUE, token TEXT UNIQUE, data TEXT)"
        db.execute(sql)
        db.commit()

        sql = "create table devices (name TEXT NOT NULL UNIQUE, email TEXT, ping_at TEXT, set_at TEXT, relay_id TEXT)"
        db.execute(sql)
        db.commit()

        db.close()


def open_db():
    init_database()
    return sqlite3.connect(db_path)


def close_db(db):
    db.close()


def query_db(db, query, args=(), one=False):
    cur = db.execute(query, args)
    rv = [dict((cur.description[idx][0], value)
               for idx, value in enumerate(row)) for row in cur.fetchall()]
    return (rv[0] if rv else None) if one else rv


def exec_db(db, query):
    db.execute(query)
    if not query.startswith('SELECT'):
        db.commit()


def add_user(db, email: str):
    sql = f"INSERT INTO users(email) VALUES ('{email}')"

    try:
        exec_db(db, sql)
    except Exception as exc:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print("ERROR adding user to db on line {}!\n\t{}".format(exc_tb.tb_lineno, exc), flush=True)


def delete_user(db, email: str,):
    sql = f"DELETE FROM users WHERE email = '{email}'"

    try:
        exec_db(db, sql)
    except Exception as exc:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print("ERROR removing user from db on line {}!\n\t{}".format(exc_tb.tb_lineno, exc), flush=True)


def get_user(db, email: str = None, token: str = None):
    one = True
    if email:
        sql = f"SELECT * FROM users WHERE email = '{email}'"
    elif token:
        sql = f"SELECT * FROM users WHERE token = '{token}'"
    else:
        one = False
        sql = "SELECT * FROM users"

    try:
        user = query_db(db, sql, one=one)
    except Exception as exc:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print(f"ERROR reading data on line {exc_tb.tb_lineno}!\n\t{exc}", flush=True)
        user = None

    return user


def update_user(db, email: str, token: str = None, password: str = None, data: str = None):
    user = get_user(db=db, email=email)

    if user:
        if token is not None:
            user["token"] = token
        if password:
            user["password"] = password
        if data is not None:
            user["data"] = data

        sql = "UPDATE users SET token = '{}', password = '{}', data = '{}' WHERE email = '{}'" \
              "".format(user["token"], user["password"], user["data"], email)

        try:
            exec_db(db, sql)
        except Exception as exc:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print("ERROR updating user in db on line {}!\n\t{}".format(exc_tb.tb_lineno, exc), flush=True)


def add_device(db, name: str):
    sql = f"INSERT INTO devices (name, email) VALUES ('{name}', 'None')"

    try:
        exec_db(db, sql)
    except Exception as exc:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print("ERROR adding device to db on line {}!\n\t{}".format(exc_tb.tb_lineno, exc), flush=True)


def get_device(db, name: str = None, email: str = None):
    if name is not None:
        sql = f"SELECT * FROM devices WHERE name = '{name}'"
        one = True
    else:
        #  Make sure to store in database emails surrounded with '|' to prevent
        #  matching emails containing the requested one.
        sql = f"SELECT * FROM devices WHERE email LIKE '%|{email}|%'"
        one = False

    try:
        device = query_db(db, sql, one=one)
    except Exception as exc:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print(f"ERROR reading data on line {exc_tb.tb_lineno}!\n\t{exc}", flush=True)
        device = None

    return device


def update_device(db, name: str, ping_at: str = None, set_at: str = None, relay_id: str = None, email: str = None):
    device = get_device(db=db, name=name)

    if device:
        if email:
            sql = "UPDATE devices SET email = '{}' WHERE name = '{}'".format(email, name)
        elif ping_at:
            sql = "UPDATE devices SET ping_at = '{}' WHERE name = '{}'".format(ping_at, name)
        else:
            sql = "UPDATE devices SET set_at = '{}', relay_id = '{}' WHERE name = '{}'".format(set_at, relay_id, name)

        try:
            exec_db(db, sql)
        except Exception as exc:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print("ERROR updating user in db on line {}!\n\t{}".format(exc_tb.tb_lineno, exc), flush=True)


def delete_device(db, name: str):
    sql = f"DELETE FROM devices WHERE name = '{name}'"

    try:
        exec_db(db, sql)
    except Exception as exc:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print("ERROR removing device from db on line {}!\n\t{}".format(exc_tb.tb_lineno, exc), flush=True)
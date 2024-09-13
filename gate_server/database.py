import sys
import settings
import pymysql
import os

pymysql.install_as_MySQLdb()

current_path = os.path.dirname(os.path.realpath(__file__))
db_path = os.path.join(current_path, "database.db")


def open_db():
    connection = pymysql.connect(
        host=settings.DB_HOST,
        user=settings.DB_USER,
        passwd=settings.DB_PASS,
        database=settings.DB_NAME
    )
    db_cursor = connection.cursor(buffered=True)
    return (connection, db_cursor)


def close_db(connection, db_cursor):
    db_cursor.close()
    connection.close()


def init_database(connection, db_cursor):

    sql = "create table users (email TEXT NOT NULL UNIQUE, token TEXT UNIQUE, data TEXT)"
    db_cursor.execute(sql)

    sql = "create table devices (name TEXT NOT NULL UNIQUE, email TEXT, ping_at TEXT, set_at TEXT, relay_id TEXT)"
    db_cursor.execute(sql)
    connection.commit()


def add_user(connection, db_cursor, email: str):
    sql = f"INSERT INTO users(email) VALUES ('{email}',)"

    try:
        db_cursor.execute(sql)
        connection.commit()
    except Exception as exc:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print("ERROR adding user to db on line {}!\n\t{}".format(exc_tb.tb_lineno, exc), flush=True)


def delete_user(connection, db_cursor, email: str):
    sql = f"DELETE FROM users WHERE email = '{email}'"

    try:
        db_cursor.execute(sql)
        connection.commit()
    except Exception as exc:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print("ERROR removing user from db on line {}!\n\t{}".format(exc_tb.tb_lineno, exc), flush=True)


def get_user(connection, db_cursor, email: str = None, token: str = None):
    one = True
    if email:
        sql = f"SELECT * FROM users WHERE email = '{email}'"
    elif token:
        sql = f"SELECT * FROM users WHERE token = '{token}'"
    else:
        sql = f"SELECT * FROM users"
        one = False

    user = None
    try:
        db_cursor.execute(sql)
        if one:
            user = db_cursor.fetchone()
        else:
            user = db_cursor.fetchall()
    except Exception as exc:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print(f"ERROR reading data on line {exc_tb.tb_lineno}!\n\t{exc}", flush=True)

    return user


def update_user(connection, db_cursor, email: str, token: str = None, password: str = None, data: str = None):
    user = get_user(connection, db_cursor, email=email)

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
            db_cursor.execute(sql)
            connection.commit()
        except Exception as exc:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print("ERROR updating user in db on line {}!\n\t{}".format(exc_tb.tb_lineno, exc), flush=True)


def add_device(connection, db_cursor, name: str):
    sql = f"INSERT INTO devices (name, email) VALUES ('{name}', 'None')"

    try:
        db_cursor.execute(sql)
        connection.commit()
    except Exception as exc:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print("ERROR adding device to db on line {}!\n\t{}".format(exc_tb.tb_lineno, exc), flush=True)


def get_device(connection, db_cursor, name: str = None, email: str = None):
    one = True
    if name:
        sql = f"SELECT * FROM devices WHERE name = '{name}'"
    else:
        sql = f"SELECT * FROM devices WHERE email = '{email}'"
        one = False

    try:
        db_cursor.execute(sql)
        if one:
            device = db_cursor.fetchone()
        else:
            device = db_cursor.fetchall()
    except Exception as exc:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print(f"ERROR reading data on line {exc_tb.tb_lineno}!\n\t{exc}", flush=True)
        device = None

    return device


def update_device(
        connection, db_cursor,
        name: str, ping_at: str = None, set_at: str = None, relay_id: str = None, email: str = None
):
    device = get_device(connection, db_cursor, name=name)

    if device:
        if ping_at:
            sql = "UPDATE devices SET ping_at = '{}' WHERE name = '{}'".format(ping_at, name)
        if email:
            sql = "UPDATE devices SET email = '{}' WHERE name = '{}'".format(email, name)
        else:
            sql = "UPDATE devices SET set_at = '{}', relay_id = '{}' WHERE name = '{}'".format(set_at, relay_id, name)

        try:
            db_cursor.execute(sql)
            connection.commit()
        except Exception as exc:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print("ERROR updating device in db on line {}!\n\t{}".format(exc_tb.tb_lineno, exc), flush=True)


def delete_device(connection, db_cursor, name: str):
    sql = f"DELETE FROM devices WHERE name = '{name}'"

    try:
        db_cursor.execute(sql)
        connection.commit()
    except Exception as exc:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print("ERROR removing user from db on line {}!\n\t{}".format(exc_tb.tb_lineno, exc), flush=True)
import sys
import settings
import pymysql
import os

pymysql.install_as_MySQLdb()

current_path = os.path.dirname(os.path.realpath(__file__))
db_path = os.path.join(current_path, "database.db")


def check_table_exists(connection, tablename):
    cursor = connection.cursor()
    cursor.execute("SHOW TABLES LIKE '{}';".format(tablename))
    data = cursor.fetchone()
    result = False
    if data:
        result = True
    cursor.close()

    return result


def init_database(connection):
    cursor = connection.cursor()

    if not check_table_exists(connection, "users"):
        sql = "create table users (email TEXT NOT NULL UNIQUE, token TEXT UNIQUE, data TEXT)"
        cursor.execute(sql)
        connection.commit()

    if not check_table_exists(connection, "devices"):
        sql = "create table devices (name TEXT NOT NULL UNIQUE, email TEXT, ping_at TEXT, set_at TEXT, relay_id TEXT)"
        cursor.execute(sql)
        connection.commit()


def open_db():
    connection = pymysql.connect(
        host=settings.DB_HOST,
        user=settings.DB_USER,
        passwd=settings.DB_PASS,
        database=settings.DB_NAME,
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )

    return connection


def close_db(connection):
    connection.close()


def add_user(connection, email: str):
    sql = f"INSERT INTO users (email) VALUES ('{email}',)"

    print(f"ADD SQL: {sql}")
    try:
        connection.cursor().execute(sql)
        connection.commit()
    except Exception as exc:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print("ERROR adding user to db on line {}!\n\t{}".format(exc_tb.tb_lineno, exc), flush=True)


def delete_user(connection, email: str):
    sql = f"DELETE FROM users WHERE email = '{email}'"

    try:
        connection.cursor().execute(sql)
        connection.commit()
    except Exception as exc:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print("ERROR removing user from db on line {}!\n\t{}".format(exc_tb.tb_lineno, exc), flush=True)


def get_user(connection, email: str = None, token: str = None):
    one = True
    if email:
        sql = f"SELECT * FROM users WHERE email = '{email}'"
    elif token:
        sql = f"SELECT * FROM users WHERE token = '{token}'"
    else:
        sql = f"SELECT * FROM users"
        one = False

    print(f"SQL: {sql}")

    user = None
    try:
        cursor = connection.cursor()
        cursor.execute(sql)
        if one:
            user = cursor.fetchone()
        else:
            user = cursor.fetchall()
    except Exception as exc:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print(f"ERROR reading data on line {exc_tb.tb_lineno}!\n\t{exc}", flush=True)

    return user


def update_user(connection, email: str, token: str = None, password: str = None, data: str = None):
    user = get_user(connection, email=email)

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
            connection.cursor().execute(sql)
            connection.commit()
        except Exception as exc:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print("ERROR updating user in db on line {}!\n\t{}".format(exc_tb.tb_lineno, exc), flush=True)


def add_device(connection, name: str):
    sql = f"INSERT INTO devices (name, email) VALUES ('{name}', 'None')"

    try:
        connection.cursor().execute(sql)
        connection.commit()
    except Exception as exc:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print("ERROR adding device to db on line {}!\n\t{}".format(exc_tb.tb_lineno, exc), flush=True)


def get_device(connection, name: str = None, email: str = None):
    one = True
    if name:
        sql = f"SELECT * FROM devices WHERE name = '{name}'"
    else:
        sql = f"SELECT * FROM devices WHERE email = '{email}'"
        one = False

    try:
        cursor = connection.cursor()
        cursor.execute(sql)
        if one:
            device = cursor.fetchone()
        else:
            device = cursor.fetchall()
    except Exception as exc:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print(f"ERROR reading data on line {exc_tb.tb_lineno}!\n\t{exc}", flush=True)
        device = None

    return device


def update_device(
        connection, name: str, ping_at: str = None, set_at: str = None, relay_id: str = None, email: str = None
):
    device = get_device(connection, name=name)

    if device:
        if ping_at:
            sql = "UPDATE devices SET ping_at = '{}' WHERE name = '{}'".format(ping_at, name)
        if email:
            sql = "UPDATE devices SET email = '{}' WHERE name = '{}'".format(email, name)
        else:
            sql = "UPDATE devices SET set_at = '{}', relay_id = '{}' WHERE name = '{}'".format(set_at, relay_id, name)

        try:
            connection.cursor().execute(sql)
            connection.commit()
        except Exception as exc:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print("ERROR updating device in db on line {}!\n\t{}".format(exc_tb.tb_lineno, exc), flush=True)


def delete_device(connection, name: str):
    sql = f"DELETE FROM devices WHERE name = '{name}'"

    try:
        connection.cursor().execute(sql)
        connection.commit()
    except Exception as exc:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print("ERROR removing user from db on line {}!\n\t{}".format(exc_tb.tb_lineno, exc), flush=True)
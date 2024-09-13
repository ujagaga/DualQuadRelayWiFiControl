#!/usr/bin/python3
# -*- coding: utf-8 -*-

'''
pip install flask requests flask_mail
'''
from flask import Flask, g, render_template, request, flash, url_for, redirect, make_response, abort, Response, stream_with_context
from flask_mail import Message, Mail
import time
import json
import sys
import os
import settings
import database
import helper


sys.path.insert(0, os.path.dirname(__file__))

application = Flask(__name__, static_url_path='/static', static_folder='static')

application.config['SECRET_KEY'] = '9OLWxND4o83j4K4iShtef'
application.config['SESSION_COOKIE_NAME'] = 'gate_ctrl'

application.config['MAIL_SERVER'] = settings.MAIL_SERVER
application.config['MAIL_PORT'] = 465
application.config['MAIL_USERNAME'] = settings.MAIL_USERNAME
application.config["MAIL_PASSWORD"] = settings.MAIL_PASSWORD
application.config["MAIL_USE_TLS"] = False
application.config["MAIL_USE_SSL"] = False

mail = Mail(application)


@application.before_request
def before_request():
    g.db = database.open_db()


@application.teardown_request
def teardown_request(exception):
    if hasattr(g, 'db'):
        database.close_db(g.db)


@application.route('/logout')
def logout():
    token = request.cookies.get('token')
    user = database.get_user(db=g.db, token=token)
    if user:
        database.update_user(db=g.db, email=user["email"], token="")

    return redirect(url_for('index'))


@application.route('/login', methods=['GET'])
def login():
    return render_template('login.html')


@application.route('/login', methods=['POST'])
def login_post():
    email = request.form.get('email')
    password = request.form.get('password')

    user = database.get_user(db=g.db, email=email)

    if not user:
        flash('Invalid e-mail or password')
        return redirect(url_for('login'))

    encrypted_pass = helper.hash_password(password)
    if encrypted_pass != user["password"]:
        flash('Invalid e-mail or password.')
        return redirect(url_for('login'))

    token = helper.generate_token()
    database.update_user(db=g.db, email=email, token=token)

    response = make_response(redirect(url_for('index')))
    response.set_cookie('token', token)
    return response


@application.route('/device_get_status', methods=['GET'])
def device_get_status():
    args = request.args
    name = args.get("name")

    if not name:
        return "Missing 'name' parameter", 400

    relay_device = database.get_device(db=g.db, name=name)
    if not relay_device:
        unauthorized_devs = database.get_device(db=g.db, email="None")

        if len(unauthorized_devs) < 2:
            database.add_device(db=g.db, name=name)

        return "Unauthorized (Too many)", 401

    email = relay_device["email"]
    user = database.get_user(db=g.db, email=email)
    if not user:
        return "Unauthorized (No user)", 401

    # Update device ping time
    database.update_device(db=g.db, name=name, ping_at=f"{int(time.time())}")

    def stream_response():
        try:
            while True:
                # Continuously check the database for updates
                device = database.get_device(db=g.db, name=name)
                if device["set_at"] and "None" not in device["set_at"]:
                    set_timestamp = int(device["set_at"])
                    if (time.time() - set_timestamp) < settings.LIFESIGN_TIMEOUT:
                        database.update_device(db=g.db, name=name, set_at="None")
                        yield f"{device['relay_id']}\n"
                        break
                # Sleep for a short time to avoid overloading the server
                time.sleep(1)
        except GeneratorExit:
            # This is raised when the client disconnects
            print("Client disconnected")
        except Exception as e:
            print(f"Error: Streaming {e}")

    return Response(stream_with_context(stream_response()), mimetype='text/plain')


@application.route('/', methods=['GET'])
def index():
    token = request.cookies.get('token')
    if not token:
        return redirect(url_for('login'))

    user = database.get_user(db=g.db, token=token)
    if not user:
        return redirect(url_for('login'))

    data = {"prim": 4, "sec": 4}
    if user["data"] is not None and "None" not in user["data"]:
        data = json.loads(user["data"])

    connected_devices = []
    devices = database.get_device(db=g.db, email=user["email"])
    if devices:
        for device in devices:
            ping_at = device.get("ping_at")
            if ping_at and "None" not in ping_at:
                ping_time = int(ping_at)

                dev_connected = (time.time() - ping_time) < settings.LIFESIGN_TIMEOUT
                connected_devices.append({"name": device["name"], "connected": dev_connected})

    return render_template(
        'index.html',
        connected_devices=connected_devices,
        data=data
    )


@application.route('/unlock', methods=['GET'])
def unlock():
    args = request.args
    relay_index = args.get("id")

    token = request.cookies.get('token')
    if not token:
        return redirect(url_for('login'))

    user = database.get_user(db=g.db, token=token)
    if not user:
        return redirect(url_for('login'))

    devices = database.get_device(db=g.db, email=user["email"])
    if devices:
        for device in devices:
            database.update_device(db=g.db, name=device["name"], set_at=f"{int(time.time())}", relay_id=relay_index)

    return render_template('unlock.html', relay_id=relay_index)


@application.route('/reset_password', methods=['GET'])
def reset_password():
    return render_template('reset_password.html')


@application.route('/reset_password', methods=['POST'])
def reset_password_post():
    email = request.form.get('email')
    user = database.get_user(db=g.db, email=email)

    flash('If the provided e-mail address is in our database, we will send you a reset link.')
    if user:
        token = helper.generate_token()
        database.update_user(db=g.db, email=email, token=token)

        base_url = request.base_url.replace("reset_password", "set_password")

        reset_link = f"{base_url}?token={token}"
        mail_message = Message('Reset unlock portal password.', sender="do_not_reply@door.lock",
                               recipients=[email])
        mail_message.html = "<p>To reset your password, klick the following <a href='{}'>link</a>.</p>".format(
            reset_link)

        mail.send(mail_message)

    return redirect(url_for('index'))


@application.route('/set_password', methods=['GET'])
def set_password():
    args = request.args
    token = args.get("token")

    user = database.get_user(db=g.db, token=token)
    if not user:
        abort(404)

    return render_template('set_password.html', token=token)


@application.route('/set_password', methods=['POST'])
def set_password_post():
    password_1 = request.form.get('password_1')
    password_2 = request.form.get('password_2')
    token = request.form.get('token')
    user = database.get_user(db=g.db, token=token)

    if not user:
        flash("Error: Invalid token or expired link!")
        return redirect(url_for('index'))

    if password_1 != password_2:
        flash("Error: Passwords are not the same!")
        return redirect(url_for('set_password', token=token))

    ret_val = helper.validate_password(password_1)

    if ret_val == 0:
        hashed_password = helper.hash_password(password_1)
        database.update_user(db=g.db, email=user["email"], password=hashed_password)

        flash("Your password was changed successfully. You may now use it to login.")
        return redirect(url_for('login'))
    else:
        if ret_val == 0:
            flash("Error: Password can not contain empty spaces!")
        else:
            flash("Error: Password can not be shorter than 5 characters!")
        return redirect(url_for('set_password', token=token))


@application.route('/config', methods=['GET'])
def config():
    token = request.cookies.get('token')
    if not token:
        return redirect(url_for('login'))

    user = database.get_user(db=g.db, token=token)
    if not user:
        return redirect(url_for('login'))

    data = {"prim": 4, "sec": 4}
    if user["data"] and "None" not in user["data"]:
        data = json.loads(user["data"])

    return render_template('config.html', token=token, data=data)


@application.route('/config', methods=['POST'])
def config_post():
    token = request.cookies.get('token')
    if not token:
        return redirect(url_for('login'))

    user = database.get_user(db=g.db, token=token)
    if not user:
        return redirect(url_for('login'))

    prim_btn_count = request.form.get('prim')
    sec_btn_count = request.form.get('sec')
    data = {"prim": int(prim_btn_count), "sec": int(sec_btn_count)}

    database.update_user(db=g.db, email=user["email"], data=json.dumps(data))

    return redirect(url_for('index'))

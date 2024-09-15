#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
pip install flask authlib requests pymysql
'''
from flask import Flask, g, render_template, request, flash, redirect, make_response, Response, stream_with_context, url_for
import time
import json
import sys
import os
import database
import helper
from authlib.integrations.flask_client import OAuth
import logging
from logging.handlers import RotatingFileHandler
import settings

sys.path.insert(0, os.path.dirname(__file__))

logging.basicConfig(handlers=[RotatingFileHandler(os.path.join(os.path.dirname(__file__),'app.log'), maxBytes=10000, backupCount=10)],
        level=logging.DEBUG,
        format="[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s",
        datefmt='%Y-%m-%dT%H:%M:%S')

application = Flask(__name__, static_url_path='/static', static_folder='static')
application.config['SECRET_KEY'] = '9OLWxND4o83j4K4iShtef'
application.config['SESSION_COOKIE_NAME'] = 'gate_ctrl'

LIFESIGN_TIMEOUT = 20
CLIENT_SECRETS_FILE = "client_secret.json"

with open(CLIENT_SECRETS_FILE) as f:
    client_secrets = json.load(f)['web']  # Assumes the JSON structure is under 'web'

# Configure OAuth
oauth = OAuth(application)
google = oauth.register(
    name='google',
    client_id=client_secrets['client_id'],
    client_secret=client_secrets['client_secret'],
    access_token_url=client_secrets['token_uri'],
    access_token_params=None,
    authorize_url=client_secrets['auth_uri'],
    authorize_params=None,
    api_base_url='https://www.googleapis.com/oauth2/v1/',
    userinfo_endpoint='https://www.googleapis.com/oauth2/v3/userinfo',
    client_kwargs={'scope': 'email'},
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration'
)


def get_url(endpoint):
    home_url = url_for('index')
    resolved_url = url_for(endpoint).replace(home_url, '/')

    return resolved_url


@application.before_request
def before_request():
    g.db = database.open_db()


@application.teardown_request
def teardown_request(exception):
    if hasattr(g, 'db'):
        database.close_db(g.db)


@application.route('/authorize')
def authorize():
    auth_url = get_url('oauth2callback')
    return google.authorize_redirect(f"https://{request.host}{auth_url}")


@application.route('/login', methods=['GET'])
def login():
    return render_template('login.html')


@application.route('/oauth2callback')
def oauth2callback():
    google.authorize_access_token()
    resp = google.get('userinfo')
    user_info = resp.json()
    email = user_info["email"]

    user = database.get_user(connection=g.db, email=email)

    if not user:
        flash('You are not authorized to access this app. Please contact the administrator: ujagaga@gmail.com')
        return redirect(get_url('login'))

    token = helper.generate_token()
    database.update_user(connection=g.db, email=email, token=token)

    response = make_response(redirect(get_url('index')))
    response.set_cookie('token', token)
    return response


@application.route('/device_get_status', methods=['GET'])
def device_get_status():
    args = request.args
    name = args.get("name")

    if not name:
        return "Missing 'name' parameter", 400

    relay_device = database.get_device(connection=g.db, name=name)
    if not relay_device:
        unauthorized_devs = database.get_device(connection=g.db, email="None")

        if len(unauthorized_devs) < 2:
            database.add_device(connection=g.db, name=name)

        return "Unauthorized (Too many)", 401

    email = relay_device["email"]
    user = database.get_user(connection=g.db, email=email)
    if not user:
        return "Unauthorized (No user)", 401

    # Update device ping time
    database.update_device(connection=g.db, name=name, ping_at=f"{int(time.time())}")

    def stream_response():
        try:
            while True:
                # Continuously check the database for updates
                device = database.get_device(connection=g.db, name=name)
                if device["set_at"] and "None" not in device["set_at"]:
                    set_timestamp = int(device["set_at"])
                    if (time.time() - set_timestamp) < settings.LIFESIGN_TIMEOUT:
                        database.update_device(connection=g.db, name=name, set_at="None")
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
        return redirect(get_url('login'))

    user = database.get_user(connection=g.db, token=token)
    if not user:
        return redirect(get_url('login'))

    data = {"prim": 4, "sec": 4}
    if user["data"] is not None and "None" not in user["data"]:
        data = json.loads(user["data"])

    connected_devices = []
    devices = database.get_device(connection=g.db, email=user["email"])
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
        return redirect(get_url('login'))

    user = database.get_user(connection=g.db, token=token)
    if not user:
        return redirect(get_url('login'))

    devices = database.get_device(connection=g.db, email=user["email"])
    if devices:
        for device in devices:
            database.update_device(connection=g.db, name=device["name"], set_at=f"{int(time.time())}", relay_id=relay_index)

    return render_template('unlock.html', relay_id=relay_index)


@application.route('/config', methods=['GET'])
def config():
    token = request.cookies.get('token')
    if not token:
        return redirect(get_url('login'))

    user = database.get_user(connection=g.db, token=token)
    if not user:
        return redirect(get_url('login'))

    data = {"prim": 4, "sec": 4}
    if user["data"] and "None" not in user["data"]:
        data = json.loads(user["data"])

    return render_template('config.html', token=token, data=data)


@application.route('/config', methods=['POST'])
def config_post():
    token = request.cookies.get('token')
    if not token:
        return redirect(get_url('login'))

    user = database.get_user(connection=g.db, token=token)
    if not user:
        return redirect(get_url('login'))

    prim_btn_count = request.form.get('prim')
    sec_btn_count = request.form.get('sec')
    data = {"prim": int(prim_btn_count), "sec": int(sec_btn_count)}

    database.update_user(connection=g.db, email=user["email"], data=json.dumps(data))

    return redirect(get_url('index'))


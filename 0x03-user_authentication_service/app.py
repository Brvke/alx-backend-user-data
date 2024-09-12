#!/usr/bin/env python3
""" a flaskk app module """
from flask import Flask, jsonify, request, abort, redirect
import flask
from flask_cors import (CORS, cross_origin)
from auth import Auth


AUTH = Auth()
app = Flask(__name__)
CORS(app, resources={r"*": {"origins": "*"}})


@app.route('/', strict_slashes=False)
def home():
    """GET /
        RETURNS A JSONIFY RESPONSE
    """
    return flask.jsonify({"message": "Bienvenue"})


@app.route('/users', methods=['POST'], strict_slashes=False)
def users():
    """  used to create a user """
    email = request.form.get('email')
    password = request.form.get('password')

    try:
        usr = AUTH.register_user(email, password)
    except ValueError as err:
        return jsonify({"message": "email already registered"}), 400

    if usr is not None:
        return jsonify({"email": f'{email}', "message": "user created"})
    else:
        return jsonify({"message": "email already registered"}), 400


@app.route('/sessions', methods=['POST'], strict_slashes=False)
def login():
    """ used to login using session """
    email = request.form.get('email')
    password = request.form.get('password')

    if email is None or password is None:
        abort(401)

    if AUTH.valid_login(email, password):
        session = AUTH.create_session(email)
        if session:
            json = jsonify({"email": f"{email}", "message": "logged in"})
            json.set_cookie('session_id', f"{session}")
            return json
        else:
            abort(401)
    else:
        abort(401)


@app.route('/sessions', methods=['DELETE'], strict_slashes=False)
def logout():
    """ used to logout """
    c_session = request.cookies.get('session_id')
    if c_session is None:
        return abort(403)

    usr = AUTH.get_user_from_session_id(c_session)
    if usr is None:
        abort(403)

    AUTH.destroy_session(usr.id)
    return redirect('/')


@app.route('/profile', methods=['GET'], strict_slashes=False)
def profile():
    """ returns a usr using a sesion id cookie """
    c_session = request.cookies.get('session_id')
    if c_session is None:
        return abort(403)

    usr = AUTH.get_user_from_session_id(c_session)
    if usr is None:
        abort(403)

    json = jsonify({'email': f"{usr.email}"})
    json.set_cookie('session_id', f"{c_session}")
    return json, 200


@app.route('/reset_password', methods=['POST'], strict_slashes=False)
def get_reset_password_token():
    """ returns a reset token from user """
    email = request.form.get('email')
    if email is None:
        abort(403)

    try:
        token = AUTH.get_reset_password_token(email)
        return jsonify({'email': f"{email}", 'reset_token': f"{token}"}), 200
    except ValueError:
        abort(403)


@app.route('/reset_password', methods=['PUT'], strict_slashes=False)
def update_password():
    """ returns a new password """
    email = request.form.get('email')
    if email is None or not isinstance(email, str):
        abort(403)

    token = request.form.get('reset_token')
    if token is None or not isinstance(token, str):
        abort(403)

    n_pass = request.form.get('new_password')
    if n_pass is None or not isinstance(n_pass, str):
        abort(403)

    try:
        AUTH.update_password(token, n_pass)
        return jsonify({"email": f"{email}",
                        "message": "Password updated"}), 200
    except ValueError:
        abort(403)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port="5000", debug=True)

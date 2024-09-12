#!/usr/bin/env python3
""" a main module """
import requests
from auth import Auth
EMAIL = "guillaume@holberton.io"
PASSWD = "b4l0u"
NEW_PASSWD = "t4rt1fl3tt3"


def register_user(email: str, password: str) -> None:
    """ requests the register user end point """
    payload = {'email': email, 'password': password}
    r = requests.post('http://127.0.0.1:5000/users', data=payload)
    assert r.status_code == 200
    assert r.json() == {"email": email, "message": "user created"}


def log_in_wrong_password(email: str, password: str) -> None:
    """ requests with a wrong password """
    payload = {'email': email, 'password': password}
    r = requests.post("http://127.0.0.1:5000/sessions", data=payload)
    assert r.status_code == 401


def log_in(email: str, password: str) -> str:
    """ requests with correct password """
    payload = {'email': email, 'password': password}
    r = requests.post("http://127.0.0.1:5000/sessions", data=payload)
    assert r.status_code == 200
    assert r.json() == {"email": email, "message": "logged in"}
    return r.cookies['session_id']


def profile_unlogged() -> None:
    """ attempts to login without session id """
    r = requests.get('http://127.0.0.1:5000/profile')
    assert r.status_code == 403


def profile_logged(session_id: str) -> None:
    """ attempt to login with session id """
    payload = {'session_id': session_id}
    r = requests.get('http://127.0.0.1:5000/profile', cookies=payload)
    assert r.status_code == 200
    assert r.json() == {'email': EMAIL}


def log_out(session_id: str) -> None:
    """ logouts the srssion """
    payload = {'session_id': session_id}
    r = requests.delete('http://127.0.0.1:5000/sessions', cookies=payload)
    assert r.status_code == 200
    assert r.json() == {"message": "Bienvenue"}


def reset_password_token(email: str) -> str:
    """ resets a password token """
    payload = {'email': email}
    r = requests.post('http://127.0.0.1:5000/reset_password', data=payload)
    assert r.status_code == 200
    token = r.json().get('reset_token')
    assert r.json() == {'email': email, 'reset_token': token}
    return token


def update_password(email: str, reset_token: str, new_password: str) -> None:
    """ updates a password """
    payload = {'email': email,
               'reset_token': reset_token,
               'new_password': new_password}
    r = requests.put('http://127.0.0.1:5000/reset_password', data=payload)
    assert r.status_code == 200
    assert r.json() == {"email": f"{email}", "message": "Password updated"}


if __name__ == "__main__":

    register_user(EMAIL, PASSWD)
    log_in_wrong_password(EMAIL, NEW_PASSWD)
    profile_unlogged()
    session_id = log_in(EMAIL, PASSWD)
    profile_logged(session_id)
    log_out(session_id)
    reset_token = reset_password_token(EMAIL)
    update_password(EMAIL, reset_token, NEW_PASSWD)
    log_in(EMAIL, NEW_PASSWD)

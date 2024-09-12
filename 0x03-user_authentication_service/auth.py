#!/usr/bin/env python3
""" an AUTH module """
import bcrypt
from db import DB
import uuid
import user
from sqlalchemy.exc import InvalidRequestError
from sqlalchemy.orm.exc import NoResultFound


def _hash_password(password: str) -> str:
    """ has password """
    if password is None or not isinstance(password, str):
        return None

    b_pass = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashd = bcrypt.hashpw(b_pass, salt)
    return hashd.decode('utf-8')


def _generate_uuid() -> str:
    """ generates a uuid string """
    return str(uuid.uuid4())


class Auth:
    """Auth class to interact with the authentication database.
    """

    def __init__(self):
        self._db = DB()

    def register_user(self, email: str, password: str) -> user.User:
        """ used to register a user """
        if email is None or not isinstance(email, str):
            return None

        if password is None or not isinstance(password, str):
            return None

        hashd = _hash_password(password)

        kwarg = {'email': email}
        try:
            obj = self._db.find_user_by(**kwarg)
            raise ValueError(f'User {obj.email} already exists')
        except (NoResultFound, InvalidRequestError):
            usr = self._db.add_user(email, hashd)
            return usr

    def valid_login(self, email: str, password: str) -> bool:
        """ verifies the password """

        if email is None or not isinstance(email, str):
            return False

        if password is None or not isinstance(password, str):
            return False

        try:
            usr = self._db.find_user_by(email=email)
            if usr.email == email:
                b_pass = usr.hashed_password.encode('utf-8')
                b_hash = password.encode('utf-8')
                return bcrypt.checkpw(b_hash, b_pass)
            return False
        except (NoResultFound, InvalidRequestError):
            return False

    def create_session(self, u_email: str) -> str:
        """ returns an id for a session """

        if u_email is None or not isinstance(u_email, str):
            return None

        kwarg = {'email': u_email}
        try:
            usr = self._db.find_user_by(**kwarg)
            session = _generate_uuid()
            self._db.update_user(usr.id, session_id=session)
            return session
        except NoResultFound:
            return None

    def get_user_from_session_id(self, u_session: str):
        """ returns a user from session id """

        if u_session is None or not isinstance(u_session, str):
            return None

        try:
            usr = self._db.find_user_by(session_id=u_session)
            return usr
        except NoResultFound:
            return None

    def destroy_session(self, user_id: int):
        """ destroyes a session_id of a user class """
        if user_id is None or not isinstance(user_id, int):
            return None

        kwargs = {'id': user_id}
        try:
            usr = self._db.find_user_by(**kwargs)
            self._db.update_user(usr.id, session_id=None)
        except NoResultFound:
            return None

    def get_reset_password_token(self, u_email: str) -> str:
        """ used to reset the password """

        if u_email is None or not isinstance(u_email, str):
            return None

        try:
            usr = self._db.find_user_by(email=u_email)
            token = _generate_uuid()
            self._db.update_user(usr.id, reset_token=token)
            return token
        except NoResultFound:
            raise ValueError

    def update_password(self, token: str, u_password: str):
        """ updates password """
        if token is None or not isinstance(token, str):
            return None

        if u_password is None or not isinstance(u_password, str):
            return None

        try:
            usr = self._db.find_user_by(reset_token=token)
        except NoResultFound:
            raise ValueError

        b_pass = _hash_password(u_password)
        self._db.update_user(usr.id, hashed_password=b_pass, reset_token=None)
        return None

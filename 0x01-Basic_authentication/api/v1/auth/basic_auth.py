#!/usr/bin/env python3
""" a module for the basic_auth class """
from api.v1.auth.auth import Auth
from models.user import User
from typing import TypeVar
import base64
import binascii


class BasicAuth(Auth):
    """ expand the Auth class """
    def extract_base64_authorization_header(self,
                                            authorization_header: str) -> str:
        """ returns Base64 part of authorization header """
        if authorization_header is None:
            return None
        elif not isinstance(authorization_header, str):
            return None

        head_list = authorization_header.split()
        if head_list[0] != 'Basic':
            return None
        else:
            return head_list[1]

    def decode_base64_authorization_header(
            self,
            base64_authorization_header: str) -> str:
        """ decodes an str encoded base_64 object """

        if base64_authorization_header is None:
            return None

        if not isinstance(base64_authorization_header, str):
            return None

        bytes64 = bytes(base64_authorization_header, "utf-8")
        try:
            return base64.b64decode(bytes64).decode("utf-8")
        except binascii.Error:
            return None

    def extract_user_credentials(
         self,
         decoded_base64_authorization_header: str) -> (str, str):
        """ returns username and value from base64 """
        if decoded_base64_authorization_header is None:
            return (None, None)

        if not isinstance(decoded_base64_authorization_header, str):
            return (None, None)

        if ":" not in decoded_base64_authorization_header:
            return (None, None)

        auth64 = decoded_base64_authorization_header.split(":")
        auth64[1] = ":".join(auth64[i] for i in range(1, len(auth64)))

        return (auth64[0], auth64[1])

    def user_object_from_credentials(self, user_email: str,
                                     user_pwd: str) -> TypeVar('User'):
        """ returns user instance based on email and password """
        if user_email is None or not isinstance(user_email, str):
            return None

        if user_pwd is None or not isinstance(user_pwd, str):
            return None

        try:
            u_list = []
            u_list = User.search({'email': user_email})
        except KeyError:
            None

        if len(u_list) == 0:
            return None

        u = u_list[0]
        if u.is_valid_password(user_pwd) is False:
            return None
        else:
            return u

    def current_user(self, request=None) -> TypeVar('User'):
        """ user instance of a request """

        Authorization = self.authorization_header(request)
        if Authorization is None:
            return None

        credentials = self.extract_base64_authorization_header(Authorization)
        if credentials is None:
            return None

        base64 = self.decode_base64_authorization_header(credentials)
        if base64 is None:
            return None

        user_info = self.extract_user_credentials(base64)
        if None in user_info:
            return None

        user = self.user_object_from_credentials(user_info[0], user_info[1])
        if user is None:
            return None
        return user

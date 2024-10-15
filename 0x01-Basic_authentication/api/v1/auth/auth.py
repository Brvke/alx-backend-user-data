#!/usr/bin/env python3
""" a module for the Auth class """
import requests
from typing import List, TypeVar
from flask import Flask


class Auth:
    """ a class to manage the API authentication """
    def require_auth(self, path: str, excluded_paths: List[str]) -> bool:
        """ requires auth """
        if path is None or excluded_paths is None:
            return True

        if path[-1] != '/':
            path = path + '/'

        for i in excluded_paths:
            if i[-1] == '*':
                if path[:len(i) - 1] == i[:-1]:
                    return False
            else:
                if path == i:
                    return False
        return True

    def authorization_header(self, request=None) -> str:
        """ authorizes header """
        if request is None:
            return None

        key = request.headers.get('Authorization')
        if key is None:
            return None
        return key

    def current_user(self, request=None) -> TypeVar('User'):
        """ current_user """
        return None

#!/usr/bin/env python3
""" encrypts a password """
import bcrypt


def hash_password(password: str) -> bytes:
    """ retunes a salted has of the input string """
    pasw = str.encode(password)
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(pasw, salt)


def is_valid(encrypted_password: bytes, password: str) -> bool:
    """ checks if a string a password is same as a hashed pass """
    passw = str.encode(password)
    return bcrypt.checkpw(passw, encrypted_password)

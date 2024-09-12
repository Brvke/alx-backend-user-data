#!/usr/bin/env python3
"""DB module
"""
from sqlalchemy import create_engine
from sqlalchemy.exc import InvalidRequestError
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.session import Session

from user import Base, User


class DB:
    """DB class
    """

    def __init__(self) -> None:
        """Initialize a new DB instance
        """
        self._engine = create_engine("sqlite:///a.db", echo=False)
        Base.metadata.drop_all(self._engine)
        Base.metadata.create_all(self._engine)
        self.__session = None

    @property
    def _session(self) -> Session:
        """Memoized session object
        """
        if self.__session is None:
            DBSession = sessionmaker(bind=self._engine)
            self.__session = DBSession()
        return self.__session

    def add_user(self, email: str, hashed_password: str) -> User:
        """ adds email and hashed_password to the database """
        if email is None or not isinstance(email, str):
            return None

        if hashed_password is None or not isinstance(hashed_password, str):
            return None

        user = User()
        user.email = email
        user.hashed_password = hashed_password
        self._session.add(user)
        self._session.commit()
        return user

    def find_user_by(self, **kwargs) -> User:
        """ returns a user by the """
        columns = User.__table__.columns.keys()
        all_users = self._session.query(User).all()
        flag = False
        for k, v in kwargs.items():
            if k in columns:
                for usr in all_users:
                    if getattr(usr, k) == v:
                        flag = True
                        return usr
                if flag is False:
                    raise NoResultFound
            else:
                raise InvalidRequestError
        raise InvalidRequestError

    def update_user(self, user_id: int, **kwargs) -> None:
        """ updates a user instance """

        if user_id is None or not isinstance(user_id, int):
            return None

        try:
            obj = self.find_user_by(id=user_id)
        except (NoResultFound, InvalidRequestError):
            return None

        for k, v in kwargs.items():
            if k in obj.__dict__:
                setattr(obj, k, v)
            else:
                raise ValueError
        return None

#!/usr/bin/env python3
""" a module for filter datum function """
import logging
import mysql.connector
import os
import re
import bcrypt
PII_FIELDS = ('password', "email", 'ssn', 'ip', 'phone')


def get_db() -> mysql.connector.connection.MySQLConnection:
    """ create a mysql connection using enviroment vairables """
    user = os.environ.get('PERSONAL_DATA_DB_USERNAME', 'root')
    password = os.environ.get('PERSONAL_DATA_DB_PASSWORD', '')
    host = os.environ.get('PERSONAL_DATA_DB_HOST', 'localhost')
    database = os.environ['PERSONAL_DATA_DB_NAME']

    connection = mysql.connector.connect(host=host,
                                         user=user,
                                         password=password,
                                         database=database)
    return connection


def filter_datum(fields: list, redaction: str,
                 message: str, separator: str) -> str:
    """ a filter datum  function """
    for field in fields:
        message = re.sub(f'(?<={field}=).*?(?=;)', redaction, message)
    return message


def get_logger() -> logging.Logger:
    """ a function to rturn a logging object """
    logger = logging.getLogger('user_data')
    logger.setLevel(logging.INFO)
    logger.propagate = False
    handler = logging.StreamHandler()
    formatter = RedactingFormatter(fields=PII_FIELDS)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger


def main():
    """ main function to retrive info from database """
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute('SELECT * FROM users;')
    for row in cursor:
        message = ";".join(f"{key}={value}" for key, value in row.items())
        log_record = logging.LogRecord("user_data", logging.INFO, None, None,
                                       message, None, None)
        formatter = RedactingFormatter(fields=("name", "email",
                                               "ssn", "password", "phone"))
        print(formatter.format(log_record))


class RedactingFormatter(logging.Formatter):
    """ Redacting Formatter class
        """

    REDACTION = "***"
    FORMAT = "[HOLBERTON] %(name)s %(levelname)s %(asctime)-15s: %(message)s"
    SEPARATOR = ";"

    def __init__(self, *args, **kwargs):
        """ initalizes class instances """
        if "fields" in kwargs.keys():
            self.fields = kwargs["fields"]
        logging.basicConfig(format=self.FORMAT)
        super(RedactingFormatter, self).__init__(self.FORMAT)

    def format(self, record: logging.LogRecord) -> str:
        """ uses filter datum to filter the record """
        message = super(RedactingFormatter, self).format(record)
        records = filter_datum(self.fields, self.REDACTION,
                               message, self.SEPARATOR)
        return records


if __name__ == '__main__':

    main()
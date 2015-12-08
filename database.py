# Libraries
from google.appengine.ext import ndb
import hashlib


user_key = ndb.Key('User', 'default_user')


# Data model
class User(ndb.Model):
    name = ndb.TextProperty(indexed=True)
    password = ndb.TextProperty()
    email = ndb.TextProperty(indexed=True)
    date = ndb.DateTimeProperty(auto_now_add=True)
    photo = ndb.BlobProperty()


# Manages users: create, delete, select, modify
class UserManager:
    def __init__(self):
        pass

    @staticmethod
    def create(username, password, email, photo):
        user = User(parent=user_key)

        user.name = username
        user.password = hashlib.md5(password).hexdigest()
        user.email = email
        user.photo = photo

        user.put()
        return True;

    @staticmethod
    def select():
        users = ndb.gql(
            'SELECT * '
            'FROM User '
            'WHERE ANCESTOR IS :1 '
            'ORDER BY date DESC',
            user_key
        )

        return users

    @staticmethod
    def select_by_username(username):
        user = ndb.gql(
            'SELECT * '
            'FROM User '
            'WHERE name = :1 '
            'ORDER BY date DESC',
            username
        )
        return user.get()

    @staticmethod
    def select_by_email(email):
        user = ndb.gql(
            'SELECT * '
            'FROM User '
            'WHERE email = :1 '
            'ORDER BY date DESC',
            email
        )
        return user.get()

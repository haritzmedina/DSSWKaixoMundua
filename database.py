# Libraries
from google.appengine.ext import ndb
import hashlib

import logging

user_key = ndb.Key('User', 'default_user')
photo_key = ndb.Key('Photo', 'default_photo')
install_key = ndb.Key('Install', 'default_installation')


# Data model
class User(ndb.Model):
    name = ndb.TextProperty(indexed=True)
    password = ndb.TextProperty()
    email = ndb.TextProperty(indexed=True)
    date = ndb.DateTimeProperty(auto_now_add=True)
    photo = ndb.TextProperty()  # Profile photo url
    background = ndb.TextProperty() # Web page background image
    roleLevel = ndb.IntegerProperty()  # 0 not activated, 1 activated by user, 2 activated by admin, 3 admin account
    attempts = ndb.IntegerProperty()  # Number of attempts before blocking the account


class Photo(ndb.Model):
    owner = ndb.KeyProperty(kind=User, indexed=True)
    privacy = ndb.IntegerProperty(indexed=True)
    date = ndb.DateTimeProperty(auto_now_add=True)
    name = ndb.TextProperty()
    image = ndb.BlobKeyProperty()


class Album(ndb.Model):
    owner = ndb.KeyProperty(kind=User, repeated=True)
    name = ndb.TextProperty(indexed=True)


class AlbumPhoto(ndb.Model):
    album = ndb.KeyProperty(kind=Album, repeated=True)
    photo = ndb.KeyProperty(kind=Photo, repeated=True)


class PhotoUserVisualization(ndb.Model):
    photo = ndb.KeyProperty(kind=Photo, repeated=True)
    user = ndb.KeyProperty(kind=User, repeated=True)


class PhotoViews(ndb.Model):
    user = ndb.TextProperty(indexed=True)
    photo = ndb.TextProperty(indexed=True)


class Install(ndb.Model):
    installed = ndb.BooleanProperty()


# Installation management
class InstallManager:
    def __init__(self):
        pass

    @staticmethod
    def install():
        install = Install(parent=install_key)
        install.installed = True

        key = install.put()
        return key.id()

    @staticmethod
    def isInstalled():
        installed = ndb.gql(
                'SELECT * '
                'FROM Install '
                'WHERE installed = True '
        )
        return installed.get() is not None


# Manages users: create, delete, select, modify
class UserManager:
    def __init__(self):
        pass

    @staticmethod
    def create(username, password, email):
        return UserManager.create_user(username, password, email, roleLevel=0)

    @staticmethod
    def create_admin(username, password, email):
        return UserManager.create_user(username,password, email, roleLevel=3)

    @staticmethod
    def create_user(username, password, email, roleLevel):
        user = User(parent=user_key)

        user.name = username
        user.password = hashlib.md5(password).hexdigest()
        user.email = email
        user.roleLevel = roleLevel

        key = user.put()
        return key.id()

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

    @staticmethod
    def select_by_id(id):
        return User.get_by_id(id, parent=user_key)

class PhotosManager:
    def __init__(self):
        pass

    @staticmethod
    def createPhoto(name, owner, privacy):
        photo = Photo(parent=photo_key)

        photo.name = name
        photo.owner = owner
        photo.privacy = privacy

        return key.id()

    @staticmethod
    def retrieveAllPhotos():
        photos = ndb.gql(
            'SELECT *'
            'FROM Photo'
            'WHERE ANCESTOR IS :1 '
            'ORDER BY date DESC',
            photo_key
        )

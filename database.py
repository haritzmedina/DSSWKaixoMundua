# Libraries
import logging

from google.appengine.ext import ndb
import hashlib

user_key = ndb.Key('User', 'default_user')
photo_key = ndb.Key('Photo', 'default_photo')
install_key = ndb.Key('Install', 'default_installation')
token_key = ndb.Key('Token', 'default_token')


# Data model
class User(ndb.Model):
    name = ndb.TextProperty(indexed=True)
    password = ndb.TextProperty()
    email = ndb.TextProperty(indexed=True)
    date = ndb.DateTimeProperty(auto_now_add=True)
    photo = ndb.TextProperty()  # Profile photo url
    background = ndb.TextProperty()  # Web page background image
    role_level = ndb.IntegerProperty()  # 0 not activated, 1 activated by user, 2 activated by admin, 3 admin account
    attempts = ndb.IntegerProperty()  # Number of attempts before blocking the account


class Token(ndb.Model):
    user = ndb.KeyProperty(kind=User, indexed=True)
    date = ndb.DateTimeProperty(auto_now_add=True)
    used = ndb.BooleanProperty(default=False)


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
    def is_installed():
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
        return UserManager.create_user(username, password, email, role_level=0)

    @staticmethod
    def create_admin(username, password, email):
        return UserManager.create_user(username, password, email, role_level=3)

    @staticmethod
    def create_user(username, password, email, role_level):
        user = User(parent=user_key)

        user.name = username
        user.password = hashlib.md5(password).hexdigest()
        user.email = email
        user.role_level = role_level

        key = user.put()
        return key

    @staticmethod
    def modify_user(key,
                    username=None,
                    password=None,
                    email=None,
                    role_level=None,
                    photo=None,
                    background=None,
                    attempts=None):

        user = key.get()

        if username is not None:
            user.name = username
        if password is not None:
            user.password = password
        if email is not None:
            user.email = email
        if role_level is not None:
            user.role_level = role_level
        if photo is not None:
            user.photo = photo
        if background is not None:
            user.background = background
        if attempts is not None:
            user.attempts = attempts

        user.put()

    @staticmethod
    def remove_user(key):
        key.remove()

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


class TokenManager:
    def __init__(self):
        pass

    @staticmethod
    def create_token(user):
        token = Token(parent=token_key)
        token.user = user

        key = token.put()
        return key

    @staticmethod
    def select_token_by_id(token_id):
        return Token.get_by_id(token_id, parent=token_key)

    @staticmethod
    def set_used_token(key):
        token = key.get()
        token.used = True
        token.put()
        return token.key


class PhotosManager:
    def __init__(self):
        pass

    @staticmethod
    def createPhoto(name, owner, privacy, image_key):
        photo = Photo(parent=photo_key)

        photo.name = name
        photo.owner = owner
        photo.privacy = privacy
        photo.image = image_key

        key = photo.put()

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
        return photos

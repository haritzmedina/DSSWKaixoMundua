#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import cgi
import hashlib

import webapp2
# Jinja templates
import os
import jinja2
# Regular expression
import re
# Date time
import datetime


from google.appengine.api.blobstore import blobstore
from google.appengine.ext import vendor

# Add language compatibility
vendor.add('lib')
from webapp2_extras import i18n
from webapp2_extras.i18n import gettext as _
from language import Language
# Add database file
import database
# Add API handlers
import api
# Add email handler
import email_handler

# Sessions handler library
import session
from session import SessionManager as Session

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape', 'jinja2.ext.i18n'],
    autoescape=True)

JINJA_ENVIRONMENT.install_gettext_translations(i18n)


# Register page backend
class RegisterPage(session.BaseSessionHandler):
    def get(self):
        # Session request handler
        current_session = Session(self)
        JINJA_ENVIRONMENT.globals['session'] = current_session
        # Language request handler
        Language.language(self)
        # Check if user is already logged in
        if current_session.get_id() is not None:
            self.redirect("/")
            return None
        template = JINJA_ENVIRONMENT.get_template('static/templates/register.html')
        self.response.write(template.render())

    def post(self):
        # Session request handler
        current_session = Session(self)
        JINJA_ENVIRONMENT.globals['session'] = current_session
        # Language request handler
        Language.language(self)
        # Check if user is already logged in
        if current_session.get_id() is not None:
            self.redirect("/")
            return None
        # Retrieve request data
        username = cgi.escape(self.request.get('username'))
        password1 = cgi.escape(self.request.get('password1'))
        password2 = cgi.escape(self.request.get('password2'))
        email = cgi.escape(self.request.get('email'))

        # Load success and fail templates
        register_template = JINJA_ENVIRONMENT.get_template('static/templates/register.html')
        registered_template = JINJA_ENVIRONMENT.get_template('static/templates/registered.html')

        # Check email is well formed
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            self.response.write(register_template.render(error=_("BadEmail.")))
            return None
        # Check passwords min size is 6
        if len(password1) < 6:
            self.response.write(register_template.render(error=_("PasswordMinLengthNotReached.")))
            return None
        # Check passwords match
        if password1 != password2:
            self.response.write(register_template.render(error=_("PasswordMissmatch")))
            return None
        # Username not empty
        if len(username) < 1:
            self.response.write(register_template.render(error=_("EmptyUsername.")))
        # Check user exists
        user = database.UserManager.select_by_username(username)
        if user is not None:
            self.response.write(register_template.render(error=_("UsernameExists")))
            return None
        # Check email exists
        user = database.UserManager.select_by_email(email)
        if user is not None:
            self.response.write(register_template.render(error=_("EmailExists")))
            return None

        # Save new user in DB
        user_key = database.UserManager.create(username, password1, email)

        if user_key:
            # Create activation token
            token_key = database.TokenManager.create_token(user_key)
            # Send activation email
            email_handler.Email.send_activation(username, str(token_key.id()), email)
            # Autologin new user
            current_session.set(self, user_key.id())
            JINJA_ENVIRONMENT.globals['session'] = current_session
            self.response.write(registered_template.render(username=username))
        else:
            self.response.write(register_template.render(error=_("DatabaseError")))
            return None


# Welcome page backend
class Welcome(session.BaseSessionHandler):
    def get(self):
        # Session request handler
        current_session = Session(self)
        JINJA_ENVIRONMENT.globals['session'] = current_session
        # Language request handler
        Language.language(self)
        template = JINJA_ENVIRONMENT.get_template('static/templates/welcome.html')
        self.response.write(template.render())


# Users show page handler
class UsersPage(session.BaseSessionHandler):
    def get(self):
        # Session request handler
        current_session = Session(self)
        JINJA_ENVIRONMENT.globals['session'] = current_session
        # Language request handler
        Language.language(self)
        # Check if user is admin
        if (current_session.get_role_level() < 3):
            self.redirect("/")
            return None
        # Retrieve users
        users = database.UserManager.select()
        # Render template
        template = JINJA_ENVIRONMENT.get_template('static/templates/users.html')
        self.response.write(template.render(users=users))


# Map page handler
class MapPage(session.BaseSessionHandler):
    def get(self):
        # Session request handler
        current_session = Session(self)
        JINJA_ENVIRONMENT.globals['session'] = current_session
        # Language request handler
        Language.language(self)
        # Retrieve key
        f = open("key/googlemaps.key")
        key = f.read()
        # Render template
        template = JINJA_ENVIRONMENT.get_template('static/templates/map.html')
        self.response.write(template.render(googleApiKey=key))


# Login page handler
class LoginPage(session.BaseSessionHandler):
    def get(self):
        # Session request handler
        current_session = Session(self)
        JINJA_ENVIRONMENT.globals['session'] = current_session
        # Language request handler
        Language.language(self)
        # Check if user is already logged in
        if current_session.get_id() is not None:
            self.redirect("/")
        else:
            template = JINJA_ENVIRONMENT.get_template('static/templates/login.html')
            self.response.write(template.render())

    def post(self):
        # Session request handler
        current_session = Session(self)
        JINJA_ENVIRONMENT.globals['session'] = current_session
        # Language request handler
        Language.language(self)
        # Check if user is already logged in
        if current_session.get_id() is not None:
            self.redirect("/")
        # Language task
        Language.language(self)
        # Load form
        template = JINJA_ENVIRONMENT.get_template('static/templates/login.html')
        # Check user and password
        submitted_username = cgi.escape(self.request.get("username"))
        submitted_password = hashlib.md5(cgi.escape(self.request.get("password"))).hexdigest()
        user = database.UserManager.select_by_username(submitted_username)
        # Check user exists
        if user is not None:
            # Check if user account is blocked or not
            if user.attempts < 3:
                # Check if user and password matches
                if submitted_username == user.name and submitted_password == user.password:
                    # Session initialization
                    current_session.set(self, user.key.id())
                    # Login attempts to zero
                    database.UserManager.modify_user(user.key, attempts=0)
                    # Redirection to initial page
                    self.redirect("/")
                else:
                    # Add an attempt to user login
                    database.UserManager.modify_user(user.key, attempts=user.attempts+1)
                    self.response.write(template.render(error=_("InvalidUsernameOrPassword")))
            else:
                self.response.write(template.render(error=_("AccountBlocked")))
        else:
            self.response.write(template.render(error=_("InvalidUsernameOrPassword")))


# Photos page handler
class PhotosPage(session.BaseSessionHandler):
    def get(self):
        # Session request handler
        current_session = Session(self)
        JINJA_ENVIRONMENT.globals['session'] = current_session
        # Language request handler
        Language.language(self)
        # Create upload form
        template = JINJA_ENVIRONMENT.get_template('static/templates/photos.html')
        self.response.write(template.render())


# Profile page handler
class ProfilePage(session.BaseSessionHandler):
    def get(self, user_id):
        # Session request handler
        current_session = Session(self)
        JINJA_ENVIRONMENT.globals['session'] = current_session
        # Language request handler
        Language.language(self)

        # Retrieved user_id to integer
        user_id = int(user_id)

        user = database.UserManager.select_by_id(user_id)

        # TODO Retrieve album and send to template

        # Prompt page
        template = JINJA_ENVIRONMENT.get_template('static/templates/profile.html')
        self.response.write(template.render(user=user))


class LogoutPage(session.BaseSessionHandler):
    def get(self):
        # Session request handler
        current_session = Session(self)
        JINJA_ENVIRONMENT.globals['session'] = current_session
        # Language request handler
        Language.language(self)
        # TODO Check if user has session started
        # Logout user
        current_session.logout(self)
        # Prompt logout page
        JINJA_ENVIRONMENT.globals['session'] = current_session
        template = JINJA_ENVIRONMENT.get_template('static/templates/logout.html')
        self.response.write(template.render())


# Installation page
class InstallPage(session.BaseSessionHandler):
    def get(self):
        # Check if service is already installed
        if database.InstallManager.is_installed():
            self.redirect("/")
        else:
            template = JINJA_ENVIRONMENT.get_template('static/templates/install.html')
            self.response.write(template.render())

    def post(self):
        # Check if installation is done
        if database.InstallManager.is_installed():
            self.redirect("/")
            return None

        # Retrieve request data
        username = cgi.escape(self.request.get('username'))
        password1 = cgi.escape(self.request.get('password1'))
        password2 = cgi.escape(self.request.get('password2'))
        email = cgi.escape(self.request.get('email'))

        # Check email is well formed
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            self.response.write("Email is not well formed")
            return None
        # Check passwords min size is 6
        if len(password1) < 6:
            self.response.write("Passwords minimum length > 6")
            return None
        # Check passwords match
        if password1 != password2:
            self.response.write("Passwords do not match")
            return None
        # Username not empty
        if len(username) < 1:
            self.response.write("Username empty")
        # Check user exists
        user = database.UserManager.select_by_username(username)
        if user is not None:
            self.response.write("Username exists")
            return None
        # Create administrator user profile
        database.UserManager.create_admin(username, password1, email)
        # Installation done flag enabled
        database.InstallManager.install()
        self.response.write("Admin installation done. <a href='/'>Go welcome page</a>.")


# Account activation handler
class ActivationPage(session.BaseSessionHandler):
    def get(self, token_id):
        # Session request handler
        current_session = Session(self)
        JINJA_ENVIRONMENT.globals['session'] = current_session
        # Language request handler
        Language.language(self)
        # Load jinja template
        template = JINJA_ENVIRONMENT.get_template('static/templates/activation.html')

        # Check if token is expired
        token = database.TokenManager.select_token_by_id(int(token_id))
        if token and (datetime.datetime.now() - datetime.timedelta(days=1) < token.date) and (not token.used):
            # Activate user
            user = token.user.get()
            # Check if user is already activated
            if user.role_level > 0:
                errorMessage = _("AccountAlreadyActivated")
            else:
                errorMessage = None
            database.UserManager.modify_user(user.key, role_level=1)
            # Set token as used
            database.TokenManager.set_used_token(token.key)
        else:
            errorMessage = _("ExpiredTokenOrNotExist")
        # Prompt activation result
        self.response.write(template.render(error=errorMessage))


# TODO Remove this class
class TestPage(session.BaseSessionHandler):
    def get(self):
        photo = database.PhotosManager.get_photo_by_id(5004976929636352)
        self.response.write(photo)


class PhotoManagePage(session.BaseSessionHandler):
    def get(self, photo_id):
        # Session request handler
        current_session = Session(self)
        JINJA_ENVIRONMENT.globals['session'] = current_session
        # Language request handler
        Language.language(self)
        # Load jinja template
        template = JINJA_ENVIRONMENT.get_template('static/templates/photo.html')

        # Get photo info to display
        photo = database.PhotosManager.get_photo_by_id(int(photo_id))
        user = photo.owner.get()
        privacy = photo.privacy
        date = photo.date
        # Check if user can edit photo attributes
        edition_permission = (current_session.get_role_level() is 3) or (photo.owner == current_session.get_user_key())
        # TODO Get visualizations and albums

        # Response page
        self.response.write(template.render(
                photo_id=photo_id,
                owner=user,
                name=photo.name,
                edition_permission= edition_permission,
                date= date,
                privacy=privacy))


# If a page does not exist, return to initial page
class NotFoundPage(session.BaseSessionHandler):
    def get(self, args):
        self.redirect("/")


app = webapp2.WSGIApplication([
    ('/', Welcome),
    # Basics
    ('/install', InstallPage),
    # User management
    ('/register', RegisterPage),
    webapp2.Route('/activate/<token_id>', ActivationPage),
    ('/users', UsersPage),
    ('/login', LoginPage),
    webapp2.Route('/profile/<user_id>', ProfilePage),
    ('/logout', LogoutPage),
    # Features
    ('/map', MapPage),
    ('/photos', PhotosPage),
    webapp2.Route('/photo/<photo_id>', PhotoManagePage),
    # Photos AJAX functions
    webapp2.Route('/api/photos/manage/<option>', api.ApiPhotosManager),
    ('/api/photos/upload/path', api.ApiPhotosUploadPath),
    ('/api/photos/upload', api.ApiPhotosUpload),
    webapp2.Route('/api/photo/download/<photo_id>', api.ApiPhotoDownload),
    webapp2.Route('/api/photo/modify/<photo_id>', api.ApiPhotoModify),
    webapp2.Route('/api/photo/delete/<photo_id>', api.ApiPhotoDelete),
    ('/test', TestPage),  # TODO Remove this path
    # AJAX APIs
    webapp2.Route('/api/register/<option>/', api.ApiRegister),
    webapp2.Route('/api/map/<option>/', api.ApiMap),
    webapp2.Route('/api/user/<user_id>/<option>/', api.ApiUserManagement),
    webapp2.Route(r'/<:.*>', NotFoundPage)
], debug=True, config=session.myconfig_dict)

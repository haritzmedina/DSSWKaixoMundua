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

# Sessions handler library
from webapp2_extras import sessions
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
        # TODO check if user is already logged in
        template = JINJA_ENVIRONMENT.get_template('static/templates/register.html')
        self.response.write(template.render())

    def post(self):
        # Session request handler
        current_session = Session(self)
        JINJA_ENVIRONMENT.globals['session'] = current_session
        # Language request handler
        Language.language(self)
        # TODO check if user is already logged in
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

        user_id = database.UserManager.create(username, password1, email)
        # Save in DB
        if user_id:
            current_session.set(self, user_id)
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
        # TODO check if user is admin
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
        submittedUsername = cgi.escape(self.request.get("username"))
        submittedPassword = hashlib.md5(cgi.escape(self.request.get("password"))).hexdigest()
        user = database.UserManager.select_by_username(submittedUsername)
        if  user is not None and submittedUsername == user.name and submittedPassword == user.password:
            # Session initialization
            current_session.set(self, user.key.id())
            # Redirection to initial page
            self.redirect("/")
        else:
            self.response.write(template.render(error=_("InvalidUsernameOrPassword")))


class PhotosPage(session.BaseSessionHandler):
    def get(self):
        # Session request handler
        current_session = Session(self)
        JINJA_ENVIRONMENT.globals['session'] = current_session
        # Language request handler
        Language.language(self)
        template = JINJA_ENVIRONMENT.get_template('static/templates/photos.html')
        self.response.write(template.render())


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

# TODO Remove this class
class TestPage(session.BaseSessionHandler):
    def get(self):
        # Session request handler
        current_session = Session(self)
        JINJA_ENVIRONMENT.globals['session'] = current_session
        # Language request handler
        Language.language(self)
        self.response.write(database.UserManager.select_by_id(current_session.get_id()))

app = webapp2.WSGIApplication([
    ('/', Welcome),
    ('/register', RegisterPage),
    ('/users', UsersPage),
    ('/map', MapPage),
    ('/login', LoginPage),
    ('/photos', PhotosPage),
    ('/logout', LogoutPage),
    ('/test', TestPage),# TODO Remove this path
    webapp2.Route('/api/register/<option>/', api.ApiRegister),
    webapp2.Route('/api/map/<option>/', api.ApiMap)
], debug=True, config=session.myconfig_dict)

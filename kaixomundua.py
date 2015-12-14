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

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape', 'jinja2.ext.i18n'],
    autoescape=True)

JINJA_ENVIRONMENT.install_gettext_translations(i18n)


# Register page backend
class RegisterPage(webapp2.RequestHandler):
    def get(self):
        Language.language(self)
        template = JINJA_ENVIRONMENT.get_template('static/templates/register.html')
        self.response.write(template.render())

    def post(self):
        Language.language(self)
        # Retrieve request data
        username = self.request.get('username')
        password1 = self.request.get('password1')
        password2 = self.request.get('password2')
        email = self.request.get('email')

        # Load success and fail templates
        registerTemplate = JINJA_ENVIRONMENT.get_template('static/templates/register.html')
        registeredTemplate = JINJA_ENVIRONMENT.get_template('static/templates/registered.html')

        # Check email is well formed
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            self.response.write(registerTemplate.render(error=_("BadEmail.")))
            return None
        # Check passwords min size is 6
        if len(password1) < 6:
            self.response.write(registerTemplate.render(error=_("PasswordMinLengthNotReached.")))
            return None
        # Check passwords match
        if password1 != password2:
            self.response.write(registerTemplate.render(error=_("PasswordMissmatch")))
            return None
        # Username not empty
        if len(username) < 1:
            self.response.write(registerTemplate.render(error=_("EmptyUsername.")))
        # Check user exists
        user = database.UserManager.select_by_username(username)
        if user is not None:
            self.response.write(registerTemplate.render(error=_("UsernameExists")))
            return None
        # Check email exists
        user = database.UserManager.select_by_email(email)
        if user is not None:
            self.response.write(registerTemplate.render(error=_("EmailExists")))
            return None

        # Save in DB
        if database.UserManager.create(username, password1, email, None):
            self.response.write(registeredTemplate.render(username=username))


# Welcome page backend
class Welcome(webapp2.RequestHandler):
    def get(self):
        Language.language(self)
        template = JINJA_ENVIRONMENT.get_template('static/templates/welcome.html')
        self.response.write(template.render())


# Users show page handler
class UsersPage(webapp2.RequestHandler):
    def get(self):
        Language.language(self)
        # Retrieve users
        users = database.UserManager.select()
        # Render template
        template = JINJA_ENVIRONMENT.get_template('static/templates/users.html')
        self.response.write(template.render(users=users))

# Map page handler
class MapPage(webapp2.RequestHandler):
    def get(self):
        Language.language(self)
        # Retrieve key
        f = open("googlemaps.key")
        key = f.read()
        # Render template
        template = JINJA_ENVIRONMENT.get_template('static/templates/map.html')
        self.response.write(template.render(googleApiKey=key))


class LoginPage(webapp2.RequestHandler):
    def get(self):
        template = JINJA_ENVIRONMENT.get_template('static/templates/login.html')
        self.response.write(template.render())
    def post(self):
        # Load form
        template = JINJA_ENVIRONMENT.get_template('static/templates/login.html')
        # Check user and password
        submittedUsername = self.request.get("username")
        submittedPassword = hashlib.md5(self.request.get("password")).hexdigest()
        user = database.UserManager.select_by_username(submittedUsername)
        if submittedUsername==user.name and submittedPassword==user.password:
            self.response.write(template.render())
        else:
            self.response.write(template.render(error=_("InvalidUsernameOrPassword")))

class PhotosPage(webapp2.RequestHandler):
    def get(self):
        template = JINJA_ENVIRONMENT.get_template('static/templates/login.html')
        self.response.write(template.render())

app = webapp2.WSGIApplication([
    ('/', Welcome),
    ('/register', RegisterPage),
    ('/users', UsersPage),
    ('/map', MapPage),
    ('/login', LoginPage),
    ('/photos', PhotosPage),
    webapp2.Route('/api/register/<option>/', api.ApiRegister),
    webapp2.Route('/api/map/<option>/', api.ApiMap)
], debug=True)

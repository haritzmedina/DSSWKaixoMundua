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
# Add database file
import database
# Add API handlers
import api

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape', 'jinja2.ext.i18n'],
    autoescape=True)

JINJA_ENVIRONMENT.install_gettext_translations(i18n)


# Register page backend
class Register(webapp2.RequestHandler):
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
            self.response.write(registerTemplate.render(error=_("Bad email.")))
            return None
        # Check passwords min size is 6
        if len(password1) < 6:
            self.response.write(registerTemplate.render(error=_("Password min length not reached.")))
            return None
        # Check passwords match
        if password1 != password2:
            self.response.write(registerTemplate.render(error=_("Passwords do not match.")))
            return None
        # Username not empty
        if len(username) < 1:
            self.response.write(registerTemplate.render(error=_("Empty username.")))
        # Check user exists
        user = database.UserManager.select_by_username(username)
        if user is not None:
            self.response.write(registerTemplate.render(error=_("Username exists")))
            return None
        # Check email exists
        user = database.UserManager.select_by_email(email)
        if user is not None:
            self.response.write(registerTemplate.render(error=_("Email exists")))
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
        key = "AIzaSyCbXo4tS_T_OQj2TQ313FbNOHawoLT6lcA"
        # Render template
        template = JINJA_ENVIRONMENT.get_template('static/templates/map.html')
        self.response.write(template.render(googleApiKey=key))

# i18n language handler
class Language:
    def __init__(self):
        pass

    @staticmethod
    def setlanguage(lang):
        i18n.get_i18n().set_locale(lang)

    @staticmethod
    def language(http):
        # Language change petition
        newLang = http.request.get('language')
        cookieLang = http.request.cookies.get('language')
        currentLang = None
        if len(newLang) > 1:
            currentLang = newLang
        else:
            if cookieLang is None or len(cookieLang) < 1:
                currentLang = 'eu_ES'
            else:
                currentLang = cookieLang
        http.response.set_cookie('language', currentLang, max_age=15724800) # 26 weeks in seconds
        Language.setlanguage(currentLang)


app = webapp2.WSGIApplication([
    ('/', Welcome),
    ('/register', Register),
    ('/users', UsersPage),
    ('/map', MapPage),
    webapp2.Route('/api/register/<option>/', api.ApiRegister),
    webapp2.Route('/api/map/<option>/', api.ApiMap)
], debug=True)

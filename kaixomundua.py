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
from google.appengine.ext import vendor

vendor.add('lib')
from webapp2_extras import i18n

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape', 'jinja2.ext.i18n'],
    autoescape=True)

JINJA_ENVIRONMENT.install_gettext_translations(i18n)


class Register(webapp2.RequestHandler):
    def get(self):
        Language().setLanguage(self.request.get('language'))
        template = JINJA_ENVIRONMENT.get_template('static/templates/register.html')
        self.response.write(template.render())

    def post(self):
        # TODO check variables with python RE
        self.response.write("Not working yet")


class Welcome(webapp2.RequestHandler):
    def get(self):
        Language().setLanguage(self.request.get('language'))
        template = JINJA_ENVIRONMENT.get_template('static/templates/welcome.html')
        self.response.write(template.render())


class Language:
    def __init__(self):
        pass

    def setLanguage(self, lang):
        i18n.get_i18n().set_locale(lang)


app = webapp2.WSGIApplication([
    ('/', Welcome),
    ('/register', Register),
    ('/agurtu', Welcome),
    ('/saludo', Welcome),
    ('/greeting', Welcome)
], debug=True)

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
        i18n.get_i18n().set_locale('eu_ES')
        template = JINJA_ENVIRONMENT.get_template('static/templates/register.html')
        self.response.write(template.render())


class MainEuskera(webapp2.RequestHandler):
    def get(self):
        i18n.get_i18n().set_locale('eu_ES')
        template = JINJA_ENVIRONMENT.get_template('static/templates/welcome.html')
        self.response.write(template.render())


class MainSpanish(webapp2.RequestHandler):
    def get(self):
        preamble(self)
        self.response.out.write("<div id='message'>Hola mundo!</div>")
        info("Ver en otros idiomas:", self)


class MainEnglish(webapp2.RequestHandler):
    def get(self):
        preamble(self)
        self.response.out.write("<div id='message'>Hello world!</div>")
        info("See in other languages:", self)


def info(message, self):
    self.response.out.write(
        "<br/>"+message+"<br/>"
        "<a href='/saludo'>Castellano</a><br/><a href='/greeting'>English</a><br/><a href='/agurtu'>Euskara</a>")


def preamble(self):
    self.response.headers['Content-Type'] = 'text/html'
    self.response.out.write(
        "<html><head>"
        "<link rel='stylesheet' href='stylesheet/default.css'>"
        "<link rel='shortcut icon' href='images/h.png' type='image/x-icon'/>"
        "</head><body>")


def foot(self):
    self.response.out.write("</body></html>")

app = webapp2.WSGIApplication([
    ('/', MainEuskera),
    ('/register', Register),
    ('/agurtu', MainEuskera),
    ('/saludo', MainSpanish),
    ('/greeting', MainEnglish)
], debug=True)

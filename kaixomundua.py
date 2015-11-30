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

class MainEuskera(webapp2.RequestHandler):
    def get(self):
        preamble(self)
        self.response.out.write("<div id='message'>Kaixo Mundua!</div>")
        info("Ikusi beste lenguaietan:", self)


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
    ('/agurtu', MainEuskera),
    ('/saludo', MainSpanish),
    ('/greeting', MainEnglish)
], debug=True)

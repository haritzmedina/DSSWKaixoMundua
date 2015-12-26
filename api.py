import webapp2
# Jinja templates
import os
import jinja2
# Database access
import database
# Remote services
import urllib
# JSON library
import json
# Session handler
import session
from session import SessionManager as Session

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)


class ApiRegister(session.BaseSessionHandler):
    def get(self, option):
        template = JINJA_ENVIRONMENT.get_template('static/templates/api.json')
        if option == "emailExists":
            email = self.request.get("q")
            user = database.UserManager.select_by_email(email)
            if user is not None:
                data = '{"email": "'+email+'", "exists": true}'
            else:
                data = '{"email": "'+email+'", "exists": false}'
            result = "OK"
        elif option == "userExists":
            username = self.request.get("q")
            user = database.UserManager.select_by_username(username)
            if user is not None:
                data = '{"username": "'+username+'", "exists": true}'
            else:
                data = '{"username": "'+username+'", "exists": false}'
            result = "OK"
        else:
            data = '{"error": "Method not allowed"}'
            result = "FAIL"
        self.response.headers['Content-Type'] = 'application/json'
        self.response.write(template.render(feature="register", data=data, query=self.request.query_string, result=result))


class ApiMap(session.BaseSessionHandler):
    def get(self, option):
        template = JINJA_ENVIRONMENT.get_template('static/templates/api.json')
        if option == "searchSite":
            # Ask google maps API for location
            service_url = 'http://maps.googleapis.com/maps/api/geocode/json?'
            address = self.request.get('q')
            url = service_url + urllib.urlencode({'address': address})
            uh = urllib.urlopen(url)
            data = uh.read()
            js = json.loads(data)
            # Purge result and prepare response
            query_result = js['status']
            if query_result == "OK":
                address = js['results'][0]['formatted_address']
                lat = js['results'][0]['geometry']["location"]["lat"]
                lng = js['results'][0]['geometry']["location"]["lng"]
                data = '{"site":"'+address+'", "lat": '+str(lat)+', "lng": '+str(lng)+'}'
                result = "OK"
            elif query_result == "ZERO_RESULTS":
                data = '{"error": "Site not found"}'
                result = "FAIL"
            else:
                data = '{"error": "Unknown error"}'
                result = "FAIL"
            # Write response
            self.response.headers['Content-Type'] = 'application/json'
            self.response.write(template.render(feature="map", data=data, query=self.request.query_string, result=result))


class ApiPhotos(session.BaseSessionHandler):
    def post(self):
        # Session request handler
        current_session = Session(self)


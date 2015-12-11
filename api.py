import webapp2
# Jinja templates
import os
import jinja2
import database

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)


class ApiRegister(webapp2.RequestHandler):
    def get(self, option):
        template = JINJA_ENVIRONMENT.get_template('static/templates/api.json')
        if option == "emailExists":
            email = self.request.get("q")
            user = database.UserManager.select_by_email(email)
            if user is not None:
                data = '{"email": "'+email+'", "exists": true}'
            else:
                data = '{"email": "'+email+'", "exists": false}'
            self.response.write(template.render(feature="register", data=data, query=self.request.query_string, result="OK"))
        elif option == "userExists":
            username = self.request.get("q")
            user = database.UserManager.select_by_username(username)
            if user is not None:
                data = '{"username": "'+username+'", "exists": true}'
            else:
                data = '{"username": "'+username+'", "exists": false}'
            self.response.write(template.render(feature="register", data=data, query=self.request.query_string, result="OK"))
        else:
            data = '{"error": "Method not allowed"}'
            self.response.write(template.render(feature="register", data=data, query=self.request.query_string, result="FAIL"))


class ApiMap(webapp2.RequestHandler):
    def get(self, option):
        template = JINJA_ENVIRONMENT.get_template('static/templates/api.json')
        if option == "searchSite":
            # TODO Ask google maps API for location
            # TODO Purge result
            # TODO Prepare response
            data = '{"site":"", "lat": , "lng": }'
            # TODO Write response
            self.response.write(template.render(feature="map", data=data, query=self.request.query_string, result="OK"))






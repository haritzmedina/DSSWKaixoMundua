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

# Blobstore
from google.appengine.api.blobstore import blobstore
from google.appengine.ext import blobstore as blobstore_2

JINJA_ENVIRONMENT = jinja2.Environment(
        loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
        extensions=['jinja2.ext.autoescape'],
        autoescape=True)


class ApiRegister(session.BaseSessionHandler):
    def get(self, option):
        # Load response template
        template = JINJA_ENVIRONMENT.get_template('static/templates/api.json')
        self.response.headers['Content-Type'] = 'application/json'
        if option == "emailExists":
            email = self.request.get("q")
            user = database.UserManager.select_by_email(email)
            if user is not None:
                data = '{"email": "' + email + '", "exists": true}'
            else:
                data = '{"email": "' + email + '", "exists": false}'
            result = "OK"
        elif option == "userExists":
            username = self.request.get("q")
            user = database.UserManager.select_by_username(username)
            if user is not None:
                data = '{"username": "' + username + '", "exists": true}'
            else:
                data = '{"username": "' + username + '", "exists": false}'
            result = "OK"
        else:
            data = '{"error": "Method not allowed"}'
            result = "FAIL"
        self.response.write(template.render(feature="register",
                                            data=data,
                                            query=self.request.query_string,
                                            result=result))


class ApiMap(session.BaseSessionHandler):
    def get(self, option):
        # Load response template
        template = JINJA_ENVIRONMENT.get_template('static/templates/api.json')
        self.response.headers['Content-Type'] = 'application/json'
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
                data = '{"site":"' + address + '", "lat": ' + str(lat) + ', "lng": ' + str(lng) + '}'
                result = "OK"
            elif query_result == "ZERO_RESULTS":
                data = '{"error": "Site not found"}'
                result = "FAIL"
            else:
                data = '{"error": "Unknown error"}'
                result = "FAIL"
            # Write response
            self.response.write(template.render(feature="map",
                                                data=data,
                                                query=self.request.query_string,
                                                result=result))


class ApiPhotosUpload(session.BlobUploadSessionHandler):
    def post(self):
        # Load response template
        template = JINJA_ENVIRONMENT.get_template('static/templates/api.json')
        self.response.headers['Content-Type'] = 'application/json'
        # Session request handler
        current_session = Session(self)
        # Check if user can upload the photo
        if current_session.get_role_level() < 2:
            self.response.headers['Content-Type'] = 'application/json'
            data = '{"error": "Permission denied"}'
            result = "FAIL"
            self.response.write(template.render(feature="photo",
                                                data=data,
                                                query=self.request.query_string,
                                                result=result))
            # TODO remove photo from blob store
            return None
        # Retrieve uploaded info
        upload_files = self.get_uploads("file")
        blob_info = upload_files[0]
        # Save photo to database
        photo_id = database.PhotosManager.createPhoto("", current_session.get_user_key(), 2, blob_info.key())
        # Prompt response to user
        data = '{"photo_id": ' + str(photo_id) + '}'
        result = "OK"
        self.response.write(template.render(feature="photo", data=data, query=self.request.query_string, result=result))


class ApiPhotosUploadPath(session.BlobUploadSessionHandler):
    def get(self):
        # Load response template
        template = JINJA_ENVIRONMENT.get_template('static/templates/api.json')
        self.response.headers['Content-Type'] = 'application/json'
        # Retrieve a new session path to upload
        upload_url = blobstore.create_upload_url('/api/photos/upload')
        data = '{"url": "' + upload_url + '"}'
        self.response.write(template.render(feature="photo", data=data, query=self.request.query_string, result="OK"))


class ApiPhotoDownload(session.BlobDownloadSessionHandler):
    def get(self, photo_id):
        # Session
        current_session = Session(self)
        # Load response template
        template = JINJA_ENVIRONMENT.get_template('static/templates/api.json')

        # TODO Check visualization permissions to current user

        # Retrieve photo url for photo_id
        photo = database.PhotosManager.get_photo_by_id(int(photo_id))
        if not photo:
            self.response.write("No photo")
        elif not blobstore_2.get(photo.image):
            self.response.write("No blob")
        else:
            # TODO Count photo visited by user
            self.send_blob(photo.image)


class ApiUserManagement(session.BaseSessionHandler):
    def get(self, user_id, option):
        # Session
        current_session = Session(self)
        # Load response template
        template = JINJA_ENVIRONMENT.get_template('static/templates/api.json')
        self.response.headers['Content-Type'] = 'application/json'
        # If user is not admin and not himself, not allow to query anything
        if current_session.get_role_level() < 3 and current_session.get_id() != user_id:
            role_level = str(current_session.get_role_level())
            data = '{"error": "Permission denied' + role_level + '"}'
            result = "FAIL"
            self.response.write(template.render(feature="user",
                                                data=data,
                                                query=self.request.query_string,
                                                result=result))
            return None
        # Options
        if option == "activateAccountByAdmin":
            # Only admin is allowed to change permissions
            if current_session.get_role_level() < 3:
                data = '{"error": "You cannot change your permission level."}'
                result = "FAIL"
                self.response.write(template.render(feature="user",
                                                    data=data,
                                                    query=self.request.query_string,
                                                    result=result))
                return None
            user = database.UserManager.select_by_id(int(user_id))
            # If user not exists
            if user is None:
                data = '{"error": "User not exists."}'
                result = "FAIL"
                self.response.write(template.render(feature="user",
                                                    data=data,
                                                    query=self.request.query_string,
                                                    result=result))
                return None
            # If user has not his account activated, admin cannot active it
            if user.role_level != 1:
                data = '{"error": "User has not his account activated yet."}'
                result = "FAIL"
                self.response.write(template.render(feature="user",
                                                    data=data,
                                                    query=self.request.query_string,
                                                    result=result))
                return None
            # Activate account by admin
            database.UserManager.modify_user(user.key, role_level=2)
            data = '{"message": "Account activated by admin."}'
            result = "OK"
        elif option == "deactivateAccountByAdmin":
            # Only admin is allowed to change permissions
            if current_session.get_role_level() < 3:
                data = '{"error": "You cannot change your permission level."}'
                result = "FAIL"
                self.response.write(template.render(feature="user",
                                                    data=data,
                                                    query=self.request.query_string,
                                                    result=result))
                return None
            user = database.UserManager.select_by_id(int(user_id))
            # If user not exists
            if user is None:
                data = '{"error": "User not exists."}'
                result = "FAIL"
                self.response.write(template.render(feature="user",
                                                    data=data,
                                                    query=self.request.query_string,
                                                    result=result))
                return None
            # If user has not his account activated, admin cannot active it
            if user.role_level != 2:
                data = '{"error": "User account can not deactivated."}'
                result = "FAIL"
                self.response.write(template.render(feature="user",
                                                    data=data,
                                                    query=self.request.query_string,
                                                    result=result))
                return None
            # Activate account by admin
            database.UserManager.modify_user(user.key, role_level=1)
            data = '{"message": "Account deactivated by admin."}'
            result = "OK"
        else:
            data = '{"error": "Method not allowed"}'
            result = "FAIL"
        self.response.write(template.render(feature="user", data=data, query=self.request.query_string, result=result))


class ApiPhotosManager(session.BaseSessionHandler):
    def get(self, option):
        # Session
        current_session = Session(self)
        # Load response template
        template = JINJA_ENVIRONMENT.get_template('static/templates/api.json')
        self.response.headers['Content-Type'] = 'application/json'

        if option == "list":
            # TODO List all accesible photos
            photos = database.PhotosManager.retrieveAllPhotos()
            data = '{"photos":['
            for photo in photos:
                id = photo.key.id()
                username = photo.owner.get().name
                date = photo.date
                name = photo.name
                data += '{"photo_id": ' + str(id) + ', "username": "' + username + '", "date": "' + str(
                    date) + '", "name": "' + name + '"},'
            data = data[:-1]
            data += ']}'
            result = "OK"
        else:
            # TODO print method not allowed
            data = '{"error": "Method not allowed"}'
            result = "FAIL"
        self.response.write(template.render(feature="user", data=data, query=self.request.query_string, result=result))


class ApiPhotoModify(session.BaseSessionHandler):
    def post(self, photo_id):
        # Session
        current_session = Session(self)
        # Load response template
        template = JINJA_ENVIRONMENT.get_template('static/templates/api.json')
        self.response.headers['Content-Type'] = 'application/json'

        # TODO Review permission for this petition (only owner or admin can modify)

        photo = database.PhotosManager.get_photo_by_id(int(photo_id))

        name = self.request.get('name')
        privacy = int(self.request.get('privacy'))

        if photo is not None:
            database.PhotosManager.modify_photo(photo.key, name, privacy)
            data = '{"message": "Changes done"}'
            result = "OK"
        else:
            data = '{"error": "Photo does not exist."}'
            result = "FAIL"


        self.response.write(template.render(feature="user", data=data, query=self.request.query_string, result=result))


class ApiPhotoDelete(session.BaseSessionHandler):
    def get(self, photo_id):
        # Session
        current_session = Session(self)
        # Load response template
        template = JINJA_ENVIRONMENT.get_template('static/templates/api.json')
        self.response.headers['Content-Type'] = 'application/json'


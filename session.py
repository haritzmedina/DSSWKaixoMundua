# Import sessions for session handling
import webapp2
from webapp2_extras import sessions

# Import users database access
import database


class SessionKeyManager:
    def __init__(self):
        pass

    @staticmethod
    def get():
        f = open("key/sessionSeed.key")
        return f.read()


# This is needed to configure the session secret key
# Runs first in the whole application
myconfig_dict = {'webapp2_extras.sessions': {
    'secret_key': SessionKeyManager.get(),
}}


# Session Handling class, gets the store, dispatches the request
class BaseSessionHandler(webapp2.RequestHandler):
    def dispatch(self):
        # Get a session store for this request.
        self.session_store = sessions.get_store(request=self.request)
        try:
            # Dispatch the request.
            webapp2.RequestHandler.dispatch(self)
        finally:
            # Save all sessions.
            self.session_store.save_sessions(self.response)

    @webapp2.cached_property
    def session(self):
        # Returns a session using the default cookie key.
        return self.session_store.get_session()
        # End of BaseSessionHandler Class


# Handler for retrieving session info
class SessionManager:
    def __init__(self, http):
        # If user is logged in, retrieve user info
        if http.session.get('userid') is not None:
            self.user = database.UserManager.select_by_id(http.session.get('userid'))
        else:
            self.user = None

    def get_id(self):
        if self.user is not None:
            return self.user.key.id()
        return None

    def get_username(self):
        if self.user is not None:
            return self.user.name
        return None

    def get_role_level(http):
        if http.session.get('userid') is not None:
            # Get role level from database
            return http.session.get('userid')
        return None

    def get_user_email(http):
        if http.session.get('userid') is not None:
            # Get email from database
            return http.session.get('userid')
        return None

    def set(self, http, user_id):
        http.session['userid'] = user_id

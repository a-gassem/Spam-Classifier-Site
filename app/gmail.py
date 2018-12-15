import base64
import mimetypes
import os
import google.oauth2.credentials
import google_auth_oauthlib.flow
from apiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
from email.mime.text import MIMEText
from apiclient import errors

#file for credentials
CREDENTIALS = "credentials.json"
#file for ID
CLIENT_FILE = "client_id.json"
#scopes needed
SCOPES = {
    "send":["https://www.googleapis.com/auth/gmail.send"],
    "fetch":["https://www.googleapis.com/auth/gmail.readonly"]
    }
#name of my API application
APP_NAME = "Basic Spam Classifier"

#get credentials from storage or creates new ones via OAuth2
def get_credentials():
    #navigate to directory above application
    home_dir = os.path.abspath(
        os.path.join(os.getcwd(), os.pardir, os.pardir)
        )

    credential_dir = os.

import google.auth
from requests_oauthlib import OAuth2Session
import pickle
from google.auth.transport.urllib3 import AuthorizedHttp
import urllib3
from apiclient import errors
import httplib2shim
httplib2shim.patch()
from apiclient.discovery import build
import logging
logging.basicConfig(level=logging.DEBUG)

#https://requests-oauthlib.readthedocs.io/en/latest/examples/google.html
OAUTH_SCOPE = ['https://www.googleapis.com/auth/analytics', 
               'https://www.googleapis.com/auth/analytics.readonly',
               'https://www.googleapis.com/auth/webmasters.readonly',
               'https://www.googleapis.com/auth/spreadsheets',
               'https://www.googleapis.com/auth/drive']
CLIENT_ID='643412917207-qt8pe5hmntb9dpi5gbis2d3q8aithhhi.apps.googleusercontent.com'
CLIENT_SECRET='_UWPT3S0BFH7ONVlzHnNl4ZX'
REDIRECT_URI = 'urn:ietf:wg:oauth:2.0:oob'


# OAuth endpoints given in the Google API documentation
authorization_base_url = "https://accounts.google.com/o/oauth2/v2/auth"
token_url = "https://www.googleapis.com/oauth2/v4/token"

def auth_flow():
    auth = OAuth2Session(client_id=CLIENT_ID, scope=OAUTH_SCOPE,
                        redirect_uri=REDIRECT_URI,
                        auto_refresh_url=token_url)

    # Redirect user to Google for authorization
    authorization_url, state = auth.authorization_url(authorization_base_url,
        # offline for refresh token
        # force to always make user click authorize
        access_type="offline", prompt="select_account")
    print ('Please go here and authorize,', authorization_url)

    # Get the authorization verifier code from the callback url
    #redirect_response = raw_input('Paste the full redirect URL here:')
    code = input('Paste the code:') 

    # Fetch the access token
    auth.fetch_token(token_url, code=code, client_secret=CLIENT_SECRET)
            #authorization_response=redirect_response)
    from google_auth_oauthlib.helpers import credentials_from_session
    google_auth_credentials = credentials_from_session(auth)
    import pickle
    pickle.dump(google_auth_credentials, open('g_auth_cred.picle','wb'))
    return google_auth_credentials

google_auth_credentials = pickle.load(open("g_auth_cred.pickle",'rb'))
if not google_auth_credentials.valid:
    google_auth_credentials = auth_flow()
#import IPython
#IPython.embed()

# use urllib3 with a patch of httplib2shim
ga3 = build('analytics', 'v3', credentials=google_auth_credentials) 
ga4 = build('analytics', 'v4', credentials=google_auth_credentials) 
#print( ga3.management().accountSummaries().list().execute())









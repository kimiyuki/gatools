import numpy as np
import pandas as pd
import yaml 
from pathlib import Path
from requests_oauthlib import OAuth2Session
import pickle
from google.auth.transport.urllib3 import AuthorizedHttp
import google.auth.transport.requests
import requests
import urllib3
from apiclient import errors
import httplib2shim
httplib2shim.patch()
from apiclient import errors
from apiclient.discovery import build
from utils.jsonparse import my_dict_df
from functools import partial

import logging
logger = logging.getLogger(__name__)

try:
    from google.colab import auth as colab_auth
except:
    logger.info("I assume you are not using colab")

from .gaData import GaData
from .gscData import GscData
from .spdData import SpdData
OAUTH_SCOPE = [
    'https://www.googleapis.com/auth/analytics',
    'https://www.googleapis.com/auth/analytics.readonly',
    'https://www.googleapis.com/auth/webmasters.readonly',
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]
# it must be preferrable to use another client_id, secret 
CLIENT_ID = '643412917207-qt8pe5hmntb9dpi5gbis2d3q8aithhhi.apps.googleusercontent.com'
CLIENT_SECRET = '_UWPT3S0BFH7ONVlzHnNl4ZX'
REDIRECT_URI = 'urn:ietf:wg:oauth:2.0:oob'
AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
TOKEN_URL = "https://www.googleapis.com/oauth2/v4/token"


class SiteData:
    """google analytics, google search console data reporter"""

    def __init__(self, path=None, newUser=False):
        # Copy your credentials from the console
        # https://developers.google.com/webmaster-tools/search-console-api-original/v3/
        #for all scopes
        self.cred, self.ga3, self.ga4, self.gsc = None, None, None, None
        self.gaData, self.gscData = None, None
        assert path, "path is None: credential filepath is required"
        if newUser:
            self._get_code_auth(path)
        else:
            self._get_cred(path)
        self._build_service()
        assert self.cred.valid, "credential is invalid"
        logger.info('you need GA viewID like,\
               svc = SiteData(path="x.dat");svd.gaData.viewId=11111')

    def _build_service(self):
        """ build service for each service"""
        #cache_discovery=False to prevent "file_cache is unavailable when using oauth2client"
        _build = partial(build, cache_discovery=False, credentials=self.cred)
        self.service_ga3 = _build('analytics', 'v3')
        self.service_ga4 = _build('analytics', 'v4')
        self.service_gsc = _build('webmasters', 'v3')
        self.service_spd = _build('sheets', 'v4')
        self.service_drv = _build('drive', 'v3')
        assert all([self.service_ga3, self.service_ga4, self.service_gsc]), \
               "credentail error"
        logger.info('ga api3, ga api4, gsc, sheet, drive service are built') 
        # should I declare below vars in __init__?
        self.gaData = GaData(self.service_ga3, self.service_ga4)
        self.gscData = GscData(self.service_gsc)
        self.spdData = SpdData(self.service_spd, self.service_drv)
        return True

    def _get_cred(self, path):
        if Path(path).exists():
            self.cred = pickle.load(open(path, 'rb'))
        # https://google-auth.readthedocs.io/en/latest/reference/google.auth.transport.requests.html
        if self.cred and self.cred.expired:
            self.cred = google.oauth2.credentials.Credentials(
                token=self.cred.token, refresh_token=self.cred.refresh_token,
                token_uri=TOKEN_URL, client_id=CLIENT_ID,client_secret=CLIENT_SECRET
            )
            logger.info('refreshed')
        if self.cred is None or self.cred.valid is False:
            self._get_code_auth(path)

        pickle.dump(self.cred, open(path, 'wb'))

    def _get_code_auth(self, path):
        auth = OAuth2Session(
            client_id=CLIENT_ID,
            scope=OAUTH_SCOPE,
            redirect_uri=REDIRECT_URI,
            auto_refresh_url=TOKEN_URL)
        # offline for refresh token
        # force to always make user click authorize
        authorization_url, state = auth.authorization_url(
            AUTH_URL, access_type="offline", prompt="select_account")
        print(f"auth process state:{state}")
        print('Please go here and authorize,', authorization_url)
        try:
            code = colab_auth.getpass.getpass()
        except:
            code = input('paste the code: ')
        self._authorize(auth, code.strip())

    def _authorize(self, auth, code):
        auth.fetch_token(TOKEN_URL, code=code, client_secret=CLIENT_SECRET)
        from google_auth_oauthlib.helpers import credentials_from_session
        #TODO detect why return value does not include client_id, sercet, token_uri
        # temporarily I use google.oauth2.credentials.Credentials constructor instead.
        self.cred = credentials_from_session(auth)

    def ga_account_summary(self):
        return self.gaData.get_account_summary()

    def ga_report(self, viewId, requests, nextPageToken=None, maxreq=5):
        return self.gaData.report(viewId, requests, nextPageToken, maxreq)

    def gsc_list_sites(self):
        return self.gscData.list_sites()

    def gsc_report(self):
        return self.gscData.search_analyics()

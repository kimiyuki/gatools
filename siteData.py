import numpy as np
import pandas as pd
import yaml, os
from requests_oauthlib import OAuth2Session
import pickle
from google.auth.transport.urllib3 import AuthorizedHttp
import urllib3
from apiclient import errors
import httplib2shim
httplib2shim.patch()
from apiclient import errors
from apiclient.discovery import build
from utils.jsonparse import my_dict_df

import logging
_detail_formatting = "%(relativeCreated)08d[ms] - %(name)s - %(levelname)s - %(processName)-10s - %(threadName)s -\n*** %(message)s"
logging.basicConfig(
    level=logging.DEBUG, format=_detail_formatting, filename="log/all.log")

try:
    from google.colab import auth as colab_auth
except:
    print("I assume you are not using colab")

from gaData import GaData
from gscData import GscData
from spdData import SpdData
OAUTH_SCOPE = [
    'https://www.googleapis.com/auth/analytics',
    'https://www.googleapis.com/auth/analytics.readonly',
    'https://www.googleapis.com/auth/webmasters.readonly',
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]
# 自分の OAuth ID,SECRETがやるのが望ましいです。
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
        self.build_service()
        assert self.cred.valid, "credential is invalid"
        print('you need GA viewID like,\
               svc = SiteData(path="x.dat");svd.gaData.viewId=11111')

    def build_service(self):
        self.service_ga3 = build('analytics', 'v3', credentials=self.cred)
        self.service_ga4 = build('analytics', 'v4', credentials=self.cred)
        self.service_gsc = build('webmasters', 'v3', credentials=self.cred)
        self.service_spd = build('sheets', 'v4', credentials=self.cred)
        self.service_drv = build('drive', 'v3', credentials=self.cred)
        assert all([self.service_ga3, self.service_ga4, self.service_gsc]), \
               "credentail error"
        print('ok')
        # should I declare below vars in __init__?
        self.gaData = GaData(self.service_ga3, self.service_ga4)
        self.gscData = GscData(self.service_gsc)
        self.spdData = SpdData(self.service_spd, self.service_drv)
        return True

    def _get_cred(self, path):
        if os.path.exists(path):
            self.cred = pickle.load(open(path, 'rb'))

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
        self.cred = credentials_from_session(auth)

    def ga_account_summary(self):
        return self.gaData.get_account_summary()

    def ga_report(self, requests, nextPageToken=None, maxreq=5):
        return self.gaData.report(requests, nextPageToken, maxreq)

    def gsc_list_sites(self):
        return self.gscData.list_sites()

    def gsc_report(self):
        return self.gscData.search_analyics()

import numpy as np
import pandas as pd
import httplib2
import yaml
from apiclient import errors
from apiclient.discovery import build
from oauth2client.client import OAuth2WebServerFlow
from oauth2client import file
from oauth2client import tools 
from utils.jsonparse import my_dict_df
try:
    from google.colab import auth
except:
    print("I assume you are not using colab")

from gaData import GaData 
from gscData import GscData 
from spdData import SpdData 
OAUTH_SCOPE = ['https://www.googleapis.com/auth/analytics', 
               'https://www.googleapis.com/auth/analytics.readonly',
               'https://www.googleapis.com/auth/webmasters.readonly',
               'https://www.googleapis.com/auth/spreadsheets',
               'https://www.googleapis.com/auth/drive']
CLIENT_ID='643412917207-qt8pe5hmntb9dpi5gbis2d3q8aithhhi.apps.googleusercontent.com'
CLIENT_SECRET='_UWPT3S0BFH7ONVlzHnNl4ZX'
class SiteData:
    """google analytics, google search console data reporter"""
    def __init__(self, path=None, newUser=False):
        # Copy your credentials from the console
        #自分の OAuth ID,SECRETがやるのが望ましいです。
        self.CLIENT_ID = CLIENT_ID 
        self.CLIENT_SECRET = CLIENT_SECRET
        #https://developers.google.com/webmaster-tools/search-console-api-original/v3/ for all scopes
        self.OAUTH_SCOPE = OAUTH_SCOPE
        self.REDIRECT_URI = 'urn:ietf:wg:oauth:2.0:oob'
        self.cred, self.ga3, self.ga4, self.gsc = None,None,None,None
        self.gaData, self.gscData = None, None
        assert path, "path is None: credential filepath is required"
        if newUser:
            self._create_cred(path)
        else:
            self._get_cred(path)
        self.build_service()
        assert self.cred.invalid is False, "credential is invalid"
        print('you need GA viewID like,\
               svc = SiteData(path="x.dat");svd.gaData.viewId=11111')

    def build_service(self):
        http = self.cred.authorize(http=httplib2.Http())
        self.cred.refresh(http)
        self.service_ga4 = build('analytics', 'v4', http=http)
        self.service_ga3 = build('analytics', 'v3', http=http)
        self.service_gsc = build('webmasters', 'v3', http=http)
        self.service_spd = build('sheets', 'v4', http=http)
        self.service_drv = build('drive', 'v3', http=http)
        assert all([self.service_ga3, self.service_ga4, self.service_gsc]), "credentail error"
        print('ok')
        # should I declare below vars in __init__?
        self.gaData  = GaData(self.service_ga3, self.service_ga4)
        self.gscData = GscData(self.service_gsc)
        self.spdData = SpdData(self.service_spd, self.service_drv)
        return True 

    def _get_cred(self, path):
        storage = file.Storage(path)
        self.cred = storage.get()
        if self.cred is None or self.cred.invalid:
            self._create_cred(path)
        storage.put(self.cred)
        
        
    def _create_cred(self, path):
        flow = OAuth2WebServerFlow(self.CLIENT_ID, self.CLIENT_SECRET,self.OAUTH_SCOPE, self.REDIRECT_URI)
        print(flow.step1_get_authorize_url())
        code = input()
        self.cred = flow.step2_exchange(code.strip())
        storage = file.Storage(path)
        storage.put(self.cred)

    def create_cred_in_colab(self):
        flow = OAuth2WebServerFlow(self.CLIENT_ID, self.CLIENT_SECRET,
                                   self.OAUTH_SCOPE, self.REDIRECT_URI)
        authorize_url = flow.step1_get_authorize_url()
        print('Go to the following link in your browser: ' + authorize_url)
        #取り消したい場合は、適当な文字を入れて、実行を終わらせ。再度セルの実行をし、文字列を入れなおす
        code = auth.getpass.getpass()
        self.cred = flow.step2_exchange(code.strip())

    def ga_account_summary(self):
        return self.gaData.get_account_summary()

    def ga_report(self, requests, nextPageToken=None, maxreq=5):
        return self.gaData.report(requests, nextPageToken, maxreq)

    def gsc_list_sites(self):
        return self.gscData.list_sites()

    def gsc_report(self):
        return self.gscData.search_analyics() 


    

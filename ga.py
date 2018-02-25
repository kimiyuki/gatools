import numpy as np
import pandas as pd
import httplib2
from apiclient import errors
from apiclient.discovery import build
from oauth2client.client import OAuth2WebServerFlow
from google.colab import auth


class GA:
    def __init__(self,
            CLIENT_ID='643412917207-qt8pe5hmntb9dpi5gbis2d3q8aithhhi.apps.googleusercontent.com',
            CLIENT_SECRET='_UWPT3S0BFH7ONVlzHnNl4ZX'):
        # Copy your credentials from the console
        #自分の OAuth ID,SECRETがやるのが望ましいです。
        self.CLIENT_ID = CLIENT_ID 
        self.CLIENT_SECRET = CLIENT_SECRET
        
        # Check
        #https://developers.google.com/webmaster-tools/search-console-api-original/v3/ for all scopes
        OAUTH_SCOPE = ['https://www.googleapis.com/auth/analytics', 
                       'https://www.googleapis.com/auth/analytics.readonly',
                       'https://www.googleapis.com/auth/webmasters.readonly',
                       'https://www.googleapis.com/auth/gmail.send']
        self.OAUTH_SCOPE = OAUTH_SCOPE
                   
        # Redirect URI for installed apps4/4qWAzJo6NbPR-q2M42BbD7oYAFD4mr-mSgoH4OoSID0
        self.REDIRECT_URI = 'urn:ietf:wg:oauth:2.0:oob'
        self.service4 = None
        self.service3 = None
        self.gsc = None

    # Run through the OAuth flow and retrieve credentials
    def get_code(self):
        flow = OAuth2WebServerFlow(self.CLIENT_ID, self.CLIENT_SECRET,
                                   self.OAUTH_SCOPE, self.REDIRECT_URI)
        authorize_url = flow.step1_get_authorize_url()
        print('Go to the following link in your browser: ' + authorize_url)
        #取り消したい場合は、適当な文字を入れて、実行を終わらせ。再度セルの実行をし、文字列を入れなおす
        return auth.getpass.getpass()
    
    
    def build_service(self, code):
        flow = OAuth2WebServerFlow(self.CLIENT_ID, self.CLIENT_SECRET,
                                   self.OAUTH_SCOPE, self.REDIRECT_URI)
        credentials = flow.step2_exchange(code.strip())
        # Create an httplib2.Http object and authorize it with our credentials
        http = httplib2.Http()
        http = credentials.authorize(http)
        self.service4 = build('analytics', 'v4', http=http)
        self.serivce3 = build('analytics', 'v3', http=http)
        self.gsc = build('webmasters', 'v3', http=http)
        print("ok")
        return self.service4, self.service3, self.gsc, credentials

    
    def getData(self, requests, nextPageToken=None, maxreq=5):
      body = {}
      body["reportRequests"] = requests
      #print(body)
      ret = self.service4.reports().batchGet(body=body).execute()
      ##only to get first reports -> first requests
      rowCount = ret['reports'][0]['data']['rowCount']
      if not nextPageToken: print(rowCount) 
      yield from self._ret2DataFrame(ret['reports'])
      if 'nextPageToken' not in ret['reports'][-1]:
        return 
      else:
        nextPageToken = int(ret['reports'][-1]['nextPageToken'])
        #make requests object again with requests[0]
        requests = [requests[0]]
        requests[0]['pageSize'] = 10000
        requests[0]['pageToken'] = str(nextPageToken) #need to be STRING!
        print("nextPageToken:{}".format(nextPageToken))
        while nextPageToken + 10000 < rowCount and len(requests) < maxreq:
           new_req = requests[0].copy()
           nextPageToken = nextPageToken + 10000
           new_req['pageToken'] = str(nextPageToken) 
           requests.append(new_req)
           print("nextPageToken:{}".format(nextPageToken))
        print("batch get:{} requests".format(len(requests)))
        yield from self.getData(requests, nextPageToken)


    @staticmethod
    def get_template(view_id):
        return {
            'viewId': view_id, 
            'dateRanges': [{'startDate': '7daysAgo', 'endDate': 'yesterday'}],
            'metrics': [{'expression': 'ga:pageviews'},{'expression': 'ga:users'}],
            #'dimensions': [{'name':'ga:channelGrouping'},{'name':'ga:dimension6'}]}
            'dimensions': [{'name':'ga:channelGrouping'},{'name':'ga:deviceCategory'}]}


    @staticmethod
    def get_template_seg(view_id):
        return {
            'viewId': view_id, 
            'dateRanges': [{'startDate': '7daysAgo', 'endDate': 'yesterday'}],
            'metrics': [{'expression': 'ga:pageviews'},{'expression': 'ga:users'}],
            #'dimensions': [{'name':'ga:channelGrouping'},{'name':'ga:dimension6'}]}
            'dimensions': [{'name':'ga:deviceCategory'},{'name':'ga:segment'}],
            'segments': [{'segmentId': "sessions::condition::ga:medium=~organic"}]
        }
    
    
    def _ret2DataFrame(self, reports):
      for report in reports:
        dim_names = [x.replace("ga:","") for x in
                report.get("columnHeader").get("dimensions")]
        mtr_names = [x['name'].replace("ga:","") for x in 
                report.get("columnHeader").get("metricHeader").get("metricHeaderEntries")]
        mtr_dtypes = [x['type'].replace("ga:","") for x in 
                report.get("columnHeader").get("metricHeader").get("metricHeaderEntries")]
        mydic = {'STRING': str, "INTEGER": np.int, "FLOAT": np.float}
        dim_dtypes = [str for _ in range(len(dim_names))]
        mtr_dtypes = [mydic[x] for x in mtr_dtypes]
        dim_ind = [x['dimensions'] for x in report['data']['rows']]
        mtr_dat = np.array([x['metrics'][0]['values'] for x in report['data']['rows']])
        yield pd.concat([
            pd.DataFrame(dim_ind, columns=dim_names), 
            pd.DataFrame(mtr_dat.astype(int),columns=mtr_names)], axis=1)

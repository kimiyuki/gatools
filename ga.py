import numpy as np
import pandas as pd
import httplib2
from apiclient import errors
from apiclient.discovery import build
from oauth2client.client import OAuth2WebServerFlow
from oauth2client import file
from oauth2client import tools 
#from google.colab import auth


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
                       'https://www.googleapis.com/auth/webmasters.readonly']
     
        self.OAUTH_SCOPE = OAUTH_SCOPE
                   
        # Redirect URI for installed apps4/4qWAzJo6NbPR-q2M42BbD7oYAFD4mr-mSgoH4OoSID0
        self.REDIRECT_URI = 'urn:ietf:wg:oauth:2.0:oob'
        self.cred = None
        self.ga3 = None
        self.ga4 = None
        self.gsc = None

    def _create_cred(self):
        flow = OAuth2WebServerFlow(self.CLIENT_ID, self.CLIENT_SECRET,self.OAUTH_SCOPE, self.REDIRECT_URI)
        print(flow.step1_get_authorize_url())
        code = input()
        self.cred = flow.step2_exchange(code.strip())

    def create_cred_in_colab(self):
        flow = OAuth2WebServerFlow(self.CLIENT_ID, self.CLIENT_SECRET,
                                   self.OAUTH_SCOPE, self.REDIRECT_URI)
        authorize_url = flow.step1_get_authorize_url()
        print('Go to the following link in your browser: ' + authorize_url)
        #取り消したい場合は、適当な文字を入れて、実行を終わらせ。再度セルの実行をし、文字列を入れなおす
        code = auth.getpass.getpass()
        self.cred = flow.step2_exchange(code.strip())

    def build_service(self):
        storage = file.Storage('ga.dat')
        self.cred = storage.get()
        if self.cred is None or self.cred.invalid:
            self._create_cred() 
        http = self.cred.authorize(http=httplib2.Http())
        self.cred.refresh(http)
        self.ga4 = build('analytics', 'v4', http=http)
        self.ga3 = build('analytics', 'v3', http=http)
        self.gsc = build('webmasters', 'v3', http=http)
        assert self.ga4, "ga4 not valid"
        assert self.ga3, "ga3 not valid"
        assert self.gsc, "gsc not valid"
        print('ok')
        return True 

    
    def getData(self, requests, nextPageToken=None, maxreq=5):
      body = {}
      body["reportRequests"] = requests
      #print(body)
      ret = self.ga4.reports().batchGet(body=body).execute()
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
        yield from self.getData(requests, nextPageToken,maxreq=maxreq)


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
    

    def get_gsc_list():
        tmp = self.gsc.sites().list().execute()
        return pd.DataFrame(tmp['siteEntry'])


    def sa(url:str):
        """
        search analytics data
        thanks for code https://note.nkmk.me/python-search-console-api-download/
        TODO implements paging request
        """
        start_date = (pd.datetime.now()  - pd.Timedelta(5, 'D')).strftime("%Y-%m-%d")
        end_date = (pd.datetime.now()  - pd.Timedelta(5, 'D')).strftime("%Y-%m-%d")
        d_list = ['query', 'page']
        row_limit = 25000

        body = {
          'startDate': start_date, 'endDate': end_date,
          'dimensions': d_list,
          'rowLimit': row_limit
        }
        response = self.gsc.searchanalytics().query(siteUrl=url, body=body).execute()
        df = pd.io.json.json_normalize(response['rows'])
        for i, d in enumerate(d_list):
            df[d] = df['keys'].apply(lambda x: x[i])

        df.drop(columns='keys', inplace=True)
        return df 


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

import numpy as np
import pandas as pd
from pandas.io.json import json_normalize
import copy

class GaData:    
    def __init__(self, service_ga3, service_ga4):
        self.service_ga3 = service_ga3
        self.service_ga4 = service_ga4
        self.viewId = None

    def retrieve_imported_data_cat(self,accountId=None,webPropertyId=None): 
        """for only catalog info. 
        Google does not provide an api for downloading"""
        jsn = (self.service_ga3.management()
               .customDataSources()
               .list(accountId=accountId, webPropertyId=webPropertyId).execute())
        cat = json_normalize(jsn['items'])
        print(cat[['id', 'name']])
        return cat


    def get_account_summary(self):
        """get google analytics account summary in profile level"""
        jsn = self.service_ga3.management().accountSummaries().list().execute()
        wp = pd.io.json.json_normalize(
                jsn['items'], record_path='webProperties', meta=['id','name'], meta_prefix='ac_'
             ).drop(['kind','profiles'], axis=1)
        wp.set_index('id', inplace=True)
        profiles = pd.io.json.json_normalize(
                jsn['items'], record_path=['webProperties', 'profiles'], 
                record_prefix="profile_", meta=[['webProperties','id']]
                ).drop(['profile_kind'], axis=1)
        profiles.set_index('webProperties.id', inplace=True)
        profiles.index.name = 'id'
        return pd.merge(profiles, wp, on="id") 

    def _is_valid_request(self, req):
        #dimensions is not necessary in google API, though I put it
        KEYS = ['dateRanges', 'metrics', 'dimensions'] 
        if type(req) is not dict:
            raise TypeError
        if not all([x in req.keys() for x in KEYS]):
            print(f'at least {",".join(KEYS)} needed')
            raise ValueError
        return True

    def report(self, requests:list, nextPageToken:int=None, maxreq:int=5):
        """get data: Note: request is list of dictionary, so be carefull not to pass reference"""
        if type(requests) is dict:
            requests = [requests]
        for req in requests:
            self._is_valid_request(req)
        body = {}
        for req in requests:
            req['viewId'] = str(self.viewId)

        # use copy to prevent nextPageToken be change of the global var
        body["reportRequests"] = copy.deepcopy(requests)
        ret = self.service_ga4.reports().batchGet(body=body).execute()
        ##only to get first reports -> first requests
        rowCount = ret['reports'][0]['data']['rowCount']
        if not nextPageToken: print(f"rowCount:{rowCount}") 
        yield from self._changeToDataFrame(ret['reports'])
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
          yield from self.report(requests, nextPageToken, maxreq=maxreq)

    def _changeToDataFrame(self, reports):
        for report in reports:
            print(f"row num: {len(report['data']['rows'])}")
            dim_names = [x.replace("ga:","") for x in
                    report.get("columnHeader").get("dimensions")]
            mtr_names = [x['name'].replace("ga:","") for x in 
                    report.get("columnHeader").get("metricHeader").get("metricHeaderEntries")]
            mtr_dtypes = [x['type'].replace("ga:","") for x in 
                    report.get("columnHeader").get("metricHeader").get("metricHeaderEntries")]
            mydic = {'STRING': str, "INTEGER": np.int, "FLOAT": np.float}
            mtr_dtypes = [mydic[x] for x in mtr_dtypes]
            dim_ind = [x['dimensions'] for x in report['data']['rows']]
            mtr_dat = np.array([x['metrics'][0]['values'] for x in report['data']['rows']])
            tmp = pd.concat([
                pd.DataFrame(dim_ind, columns=dim_names), 
                pd.DataFrame(mtr_dat.astype(int),columns=mtr_names)], axis=1)
            if 'dateHour' in tmp.columns:
                tmp.index = pd.to_datetime(tmp['dateHour'], format="%Y%m%d%H")
                del tmp['dateHour']
            if 'date' in tmp.columns:
                tmp.index = pd.to_datetime(tmp['date'], format="%Y%m%d")
                del tmp['date']
            yield tmp

class GaReq():
    @staticmethod
    def get_template():
        """set request parameters"""
        return {
                'pageToken': '0',
                'dateRanges': [{'startDate': '7daysAgo', 'endDate': 'yesterday'}],
                'metrics': [{'expression': 'ga:pageviews'},{'expression': 'ga:users'}],
                #'dimensions': [{'name':'ga:channelGrouping'},{'name':'ga:dimension6'}]}
                'dimensions': [{'name':'ga:channelGrouping'},
                               {'name':'ga:dateHour'},
                               {'name':'ga:deviceCategory'},
                               {'name':'ga:userGender'}]}


    @staticmethod
    def get_template_seg():
        """set reqeust parameters about segment data""" 
        return {
            'dateRanges': [{'startDate': '7daysAgo', 'endDate': 'yesterday'}],
            'metrics': [{'expression': 'ga:pageviews'},{'expression': 'ga:users'}],
            #'dimensions': [{'name':'ga:channelGrouping'},{'name':'ga:dimension6'}]}
            'dimensions': [{'name':'ga:deviceCategory'},{'name':'ga:segment'}],
            'segments': [{'segmentId': "sessions::condition::ga:medium=~organic"}]
        }


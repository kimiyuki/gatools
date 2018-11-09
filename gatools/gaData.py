import numpy as np
import pandas as pd
from pandas.io.json import json_normalize
import copy
import functools
from dataclasses import dataclass, field
from typing import List, Any
import pickle

@dataclass
class GaRequest:
    """
    .. todo::

       add segments parameters
    """
    pageToken:int = 0
    dateRange: list = field(default_factory=lambda: ['7daysago', 'yesterday'])
    metrics:   list = field(default_factory=lambda: ['pageviews','users'])
    dimensions:list = field(default_factory=lambda: ['deviceCategory','date'])
    segments: list = field(default_factory=lambda: [])
    viewId: str = ''
    pageSize: str = 1000

    #TODO segments

    def __str__(self):
        s0 =  f"viewId: {self.viewId}"
        s1 =  f"date: {self.dateRange[0]} - {self.dateRange[1]}"
        s2 =  f"metrics: {','.join(self.metrics)}"
        s3 =  f"dimensions: {','.join(self.dimensions)}"
        s4 =  f"segments: {','.join(self.segments)}"
        s5 =  f"paging: token:{str(self.pageToken)} size:{str(self.pageSize)}"
        return "\n".join([s0, s1, s2, s3, s4, s5])


    def get(self):
        return {
                'pageToken': str(self.pageToken),
                'dateRanges': [{'startDate': self.dateRange[0],
                                'endDate': self.dateRange[1]}],
                'metrics': [{'expression': 'ga:'+x} for x in self.metrics],
                'dimensions': [{'name':'ga:'+x} for x in self.dimensions],
                'viewId': self.viewId,
                'pageSize': self.pageSize,
        }
            


class GaData:    
    def __init__(self, service_ga3, service_ga4):
        self.service_ga3 = service_ga3
        self.service_ga4 = service_ga4
        self.viewId = None

    def retrieve_imported_data_cat(self,accountId=None,webPropertyId=None): 
        """
        for only catalog info. 
        Google does not provide an api for downloading
        """
        jsn = (self.service_ga3.management()
               .customDataSources()
               .list(accountId=accountId, webPropertyId=webPropertyId).execute())
        cat = json_normalize(jsn['items'])
        print(cat[['id', 'name']])
        return cat


    def get_account_summary(self):
        """
        get google analytics account summary in profile level
        """
        jsn = self.service_ga3.management().accountSummaries().list().execute()
        wp = pd.io.json.json_normalize(
                jsn['items'], 
                record_path='webProperties', meta=['id','name'],
                meta_prefix='ac_'
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

    #@functools.lru_cache(maxsize=300)
    #def __report(self, viewid, requests:list, nextPageToken:int=None, maxreq:int=5):
    #    return pd.concat(self._report(viewid, requests, nextPageToken, maxreq))

    def report(self, 
        viewId=None, 
        requests:list=[GaRequest],
        maxreq:int=5): 
        """get data: Note: request is list of dictionary, so be carefull not to pass reference"""

        for req in requests:
            pass
            #self._is_valid_request(req) #maybe i do not need it any more
        for req in requests:
            req.viewId = str(viewId)

        # use copy to prevent nextPageToken be change of the global var
        body = {"reportRequests": copy.deepcopy([x.get() for x in requests])}
        res = self.service_ga4.reports().batchGet(body=body).execute()
        pickle.dump(res, open("log/gadata_res.pickle", 'wb'))
        #logging.log(ret)
        ##only to get first reports -> first requests
        rowCount = res['reports'][0]['data']['rowCount']
        if requests[0].pageToken == 0:
            print(f"total rows: {rowCount}")
        yield from self._changeToDataFrame(res['reports'])
        if 'nextPageToken' not in res['reports'][-1]:
            print(f"get:{rowCount} rows")
            return 
        else:
          #make requests object again with requests[0]
          newReq = copy.deepcopy(requests[0])
          newReq.pageSize = 10000
          nextPageToken = int(res['reports'][-1]['nextPageToken'])
          newReq.pageToken = str(nextPageToken)
          requests = [newReq]
          while nextPageToken + 10000 < rowCount and len(requests) < maxreq:
             req = copy.deepcopy(newReq)
             nextPageToken = nextPageToken + 10000
             req.pageToken = str(nextPageToken)
             requests.append(req)
          print(f"batch get:{len(requests)}requests: \
                 {','.join([x.pageToken for x in requests])}")
          yield from self.report(viewId, requests, maxreq=maxreq)

    def _changeToDataFrame(self, reports):
        for report in reports:
            #print(f"row num: {len(report['data']['rows'])}")
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
            if 'date' in tmp.columns:
                tmp.index = pd.to_datetime(tmp['date'], format="%Y%m%d")
                del tmp['date']
            if 'dateHour' in tmp.columns:
                tmp.index = pd.to_datetime(tmp['dateHour'], format="%Y%m%d%H")
                del tmp['dateHour']
            yield tmp




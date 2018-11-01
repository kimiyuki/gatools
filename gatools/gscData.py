import numpy as np
import pandas as pd
from typing import List

class GscData:
    """Google Search Console reporter"""
    def __init__(self, service_gsc):
        self.service_gsc = service_gsc
        self._siteUrl = None

    def list_sites(self) -> pd.DataFrame: 
        """ 
        return DF(permissionLevel, siteUrl in dataFrame of the google search console account
        """
        tmp = self.service_gsc.sites().list().execute()
        if tmp.get('siteEntry'):
            return pd.DataFrame(tmp['siteEntry'])
        else:
            print("no site entried")
            return None


    def search_analyics(self, url:str=None, start_date=None, end_date=None) -> pd.DataFrame:
        """
        search analytics data
        thanks for code https://note.nkmk.me/python-search-console-api-download/
        :returns: pandas dataframe
        
        .. todo::
        
         implements paging request

        """
        if url is None:
            url = self._siteUrl
        if start_date is None:
            start_date = (pd.datetime.now()  - pd.Timedelta(12, 'D')).strftime("%Y-%m-%d")
        if end_date is None:
            end_date = (pd.datetime.now()  - pd.Timedelta(5, 'D')).strftime("%Y-%m-%d")
        print(f"start_date:{start_date}, end_date:{end_date}")
        date_range = pd.date_range(
            pd.to_datetime(start_date), 
            pd.to_datetime(end_date), freq="D") #for if start_date is str 
        for day in date_range: 
            yield from self._search_analytics(url, day)

    def _search_analytics(self, url, day):
        d_list = ['query', 'page']
        row_limit = 25000
        body = {
          'startDate': day.strftime("%Y-%m-%d"), 
          'endDate': day.strftime("%Y-%m-%d"),
          'dimensions': d_list, 'rowLimit': row_limit
        }
        #not write a paging process yet.
        response = (self.service_gsc.searchanalytics()
                    .query(siteUrl=url, body=body).execute())
        print(f"get:{day}")
        df = pd.io.json.json_normalize(response['rows'])
        for i, d in enumerate(body['dimensions']):
            df[d] = df['keys'].apply(lambda x: x[i])

        df.drop(columns='keys', inplace=True)
        df['date'] = day 
        #pandas dataframe has the method name 'query', so rename query to q to prevent conflict 
        yield df.rename(columns={'query':'q'})



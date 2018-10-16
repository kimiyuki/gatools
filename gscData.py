import numpy as np
import pandas as pd

class GscData:
    """Google Search Console reporter"""
    def __init__(self, service_gsc):
        self.service_gsc = service_gsc
        self._siteUrl = None

    def list_sites(self):
        tmp = self.service_gsc.sites().list().execute()
        if tmp.get('siteEntry'):
            return pd.DataFrame(tmp['siteEntry'])
        else:
            print("no site entried")
            return None


    def search_analyics(self, url:str, start_date=None, end_date=None):
        """
        search analytics data
        thanks for code https://note.nkmk.me/python-search-console-api-download/
        TODO implements paging request
        """
        if start_date is None:
            start_date = (pd.datetime.now()  - pd.Timedelta(12, 'D')).strftime("%Y-%m-%d")
        if end_date is None:
            end_date = (pd.datetime.now()  - pd.Timedelta(5, 'D')).strftime("%Y-%m-%d")
        print(f"start_date:{start_date}, end_date:{end_date}")
        d_list = ['query', 'page']
        row_limit = 25000

        body = {
          'startDate': start_date, 'endDate': end_date,
          'dimensions': d_list, 'rowLimit': row_limit
        }
        response = self.service_gsc.searchanalytics().query(siteUrl=url, body=body).execute()
        df = pd.io.json.json_normalize(response['rows'])
        for i, d in enumerate(d_list):
            df[d] = df['keys'].apply(lambda x: x[i])

        df.drop(columns='keys', inplace=True)
        #pandas dataframe has the method name 'query', so rename query to q
        df = df.rename(columns={'query':'q'})
        return df 



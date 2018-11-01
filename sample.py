from gatools.siteData import SiteData
from gatools.gaData import GaRequest
import yaml
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

conf = yaml.load(open("secret_account.yaml", "r"))# chage: sample_account.yaml
ac1 = SiteData("account1.oauth") #set pathname for your google account
viewId = conf['account1']['gaview'][0]['id']

req = GaRequest()
req.dateRange[0] = '30daysago'
req.dimensions.append('dateHour')
req.dimensions.append('userGender')
req.dimensions.append('contentGroup1')
req.dimensions.append('channelGrouping')
df1 = pd.concat(ac1.gaData.report(viewId=viewId, requests=[req]))
#print(ac1.gaData.report.cache_info)
#df1.groupby('dateHour').sum()['pageviews'].plot()
(
df1
.groupby(['dateHour','userGender','contentGroup1'])
.sum()['pageviews']
.unstack(level='userGender', fill_value=0)
.assign(gender_diff = lambda x: np.log1p(x['male']) - np.log1p(x['female']))['gender_diff']
.unstack()
.loc[:, ['PDP', 'PLP', 'TOP']]
.rolling(24, min_periods=1).mean() #min_period=1 to avoid NA 
).dropna().plot()
plt.show()

ac2 = SiteData("account2.oauth")
"""
ac2.gaData.viewId = conf['account2']['gaview'][0]['id']
ac2.gscData._siteUrl = conf['account2']['gsc'][0]['siteurl'] 
df2 = pd.concat(ac2.gscData.search_analyics())
top5pages = df2.groupby('page').sum()['clicks'].nlargest(5).index.values
(df2
.query("@top5pages in page")
.groupby(['date','page']).sum()['clicks']
.unstack()
.rolling(7).mean()
).dropna().plot()
plt.show()
"""


url = 'https://www.googleapis.com/analytics/v3/metadata/ga/columns?pp=1'
import requests,json
res  = requests.get(url)
out = json.loads(res.content)
import addict,re

def select_elements(items):
    for item in out['items']:
        tp = item['attributes']['type']
        name = re.sub("ga:", '', item['id'])
        group = item['attributes']['group']
        yield (tp, name, group)

mt = pd.DataFrame.from_records(select_elements(out['items']),
    columns=['type', 'name', 'group'])

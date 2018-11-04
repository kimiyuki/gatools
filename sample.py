from gatools.siteData import SiteData
from gatools.gaData import GaRequest
import yaml
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import logging

#logging
_detail_formatting = "%(relativeCreated)08d[ms] - %(name)s - %(levelname)s \
                      - %(processName)-10s - %(threadName)s -\n*** %(message)s"
logging.basicConfig(
    level=logging.DEBUG, format=_detail_formatting, filename="log/all.log")
logging.getLogger("gatools.siteData").setLevel(level=logging.DEBUG)

# account conf
conf = yaml.load(open("secret_account.yaml", "r"))# chage: sample_account.yaml
ac1 = SiteData("account1.oauth") #set pathname for your google account
viewId = conf['account1']['gaview'][0]['id']

## google analytics
# format required request 
req = GaRequest()
req.dateRange[0] = '30daysago'
req.dimensions.append('dateHour')
req.dimensions.append('userGender')
req.dimensions.append('contentGroup1')
req.dimensions.append('channelGrouping')

# get Data
df1 = pd.concat(ac1.gaData.report(viewId=viewId, requests=[req]))
#print(ac1.gaData.report.cache_info)
#df1.groupby('dateHour').sum()['pageviews'].plot()

# data transformation 
(df1
.groupby(['dateHour','userGender','contentGroup1'])
.sum()['pageviews']
.unstack(level='userGender', fill_value=0)
.assign(gender_diff = lambda x: np.log1p(x['male']) - np.log1p(x['female']))['gender_diff']
.unstack()
.loc[:, ['PDP', 'PLP', 'TOP']]
.rolling(24, min_periods=1).mean() #min_period=1 to avoid NA 
).dropna().plot()
#plt.show()


## google search console as same above
ac2 = SiteData("account2.oauth")
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
#plt.show()

from utils.DimMetrics import DimMetExplorer, DM, MT
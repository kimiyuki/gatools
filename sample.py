from gatools.siteData import SiteData
from gatools.gaData import GaReq
import yaml
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

conf = yaml.load(open("secret_account.yaml", "r"))# chage: sample_account.yaml
REQ = GaReq.get_template()
ac1 = SiteData("account1.oauth")
ac1.gaData.viewId = conf['account1']['gaview'][0]['id']

ac2 = SiteData("account2.oauth")
ac2.gaData.viewId = conf['account2']['gaview'][0]['id']
ac2.gscData._siteUrl = conf['account2']['gsc'][0]['siteurl'] 

sp = ac2.service_spd

def main():
    df1 = pd.concat(ac1.gaData.report(REQ))
    df1.groupby('dateHour').sum()['pageviews'].plot()
    (df1
    .groupby(['dateHour','userGender'])
    .sum()['pageviews']
    .unstack()
    .rolling(24).mean()
    ).dropna().plot()
    plt.show()


    df2 = pd.concat(ac2.gscData.search_analyics())
    top5pages = df2.groupby('page').sum()['clicks'].nlargest(5).values
    (df2
    .query("@top5pages in page")
    .groupby(['date','page']).sum()['clicks']
    .unstack()
    .rolling(7).mean()
    ).dropna().plot()
    plt.show()


if __name__ == "__main__":
   pass




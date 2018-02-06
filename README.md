FOR COLABORATORY(Google's jupyter in Google Drive) USE

see this
https://colab.research.google.com/drive/1OVXOcbulNQokysQaCAofadglP44Ww6pb

ONLY IN COLABORATORY

```
#======
!rm -f ga.py
!wget https://raw.githubusercontent.com/kimiyuki/google-analytics-lib/master/ga.py
import pandas as pd
import ga
code = ga.get_code()
##=====
## separate the cells to handle oauth flow.
##=====
ga.build_service(code) #google analtics api version3, version4

VIEW_ID = "xxxxxx" 
reportRequest = {
            'viewId': VIEW_ID, 
            'dateRanges': [{'startDate': '2018-01-26', 'endDate': '2018-01-28'}],
            'metrics': [{'expression': 'ga:pageviews'},{'expression': 'ga:users'}],
            #'dimensions': [{'name':'ga:channelGrouping'},{'name':'ga:dimension6'}]}
            'dimensions': [{'name':'ga:pagePath'},{'name':'ga:dimension14'},{'name':'ga:dimension16'}]
}
ret = pd.concat( (x for x in getData([reportRequest])) )
```

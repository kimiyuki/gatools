FOR COLABORATORY(Google's jupyter in Google Drive) USE

how to use

```
#======
import ga
code = ga.get_code()
##=====
## separate the cells to handle oauth flow.
##=====
ga3, ga4 = ga.build_service(code) #google analtics api version3, version4

VIEW_ID = "xxxxxx" 
reportRequest = {
            'viewId': VIEW_ID, 
            'dateRanges': [{'startDate': '2018-01-26', 'endDate': '2018-01-28'}],
            'metrics': [{'expression': 'ga:pageviews'},{'expression': 'ga:users'}],
            #'dimensions': [{'name':'ga:channelGrouping'},{'name':'ga:dimension6'}]}
            'dimensions': [{'name':'ga:pagePath'},{'name':'ga:dimension14'},{'name':'ga:dimension16'}]
}
ret = pd.concat( (x for x in getData(ga4, [reportRequest])) )
```

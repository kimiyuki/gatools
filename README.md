FOR COLABORATORY(Google's jupyter in Google Drive) USE

see this
https://drive.google.com/file/d/1OVXOcbulNQokysQaCAofadglP44Ww6pb/view?usp=sharing

ONLY IN COLABORATORY

```
#======
!rm -f ga.py
!wget https://raw.githubusercontent.com/kimiyuki/google-analytics-lib/master/ga.py
import pandas as pd
from ga import GA
ga = GA()
code = ga.get_code()
##=====
## separate the cells to handle oauth flow.
##=====
ga4,ga3,gsc,cred = ga.build_service(code) #google analtics api version3, version4

VIEW_ID = "xxxxxx" 
req  = ga.get_template()
req['viewId'] = "xxxxxxx"
tmp = pd.concat( (x for x in ga.getData([req])) )
```

d = """
{"kind": "analytics#webPropertySummary",
 "id": "UA-27997190-1",
 "name": "0432558847.jp",
 "internalWebPropertyId": "53562517",
 "level": "STANDARD",
 "websiteUrl": "http://0432558847.jp/",
 "profiles": [
    {"kind": "analytics#profileSummary",
     "id": "54425738",
     "name": "0432558847.jp",
     "type": "WEB"},
    {"kind": "analytics#profileSummary",
     "id": "62620005",
     "name": "http://yoboushika-chiba.com",
     "type": "WEB"}]}
"""
import json
d = json.loads(d)
#import io
def my_json_parse(d: dict, prefix:str=""):
    for k, v in d.items():
        if type(v) == str:
            yield (prefix+k , v)
        elif type(v) == dict:
            yield my_json_parse(v)
        elif type(v) == list:
            # we can assume v is dict, because json???
            for x in v:
                yield from my_json_parse(x, prefix=k+"_")
                # yield my_json_parse(..) returns simply generator, so we need yield from 
        else:
            raise ValueError


out = {} 
for x in my_json_parse(d):
    if out.get(x[0]):
        out[x[0]].append(x[1])
    else:
        out[x[0]] = [x[1]]


from itertools import zip_longest
import pandas as pd
df = pd.DataFrame(
        data=list(zip_longest(*[v for _, v in out.items()])),
        columns=out.keys()
     ).fillna(method="pad")



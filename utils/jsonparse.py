#import io
import numbers, json
import pandas as pd
from itertools import zip_longest
def my_json_parse(d: dict, prefix:str=""):
    for k, v in d.items():
        if type(v) == str or isinstance(v, numbers.Number):
            yield (prefix+k , v)
        elif type(v) == dict:
            yield my_json_parse(v)
        elif type(v) == list:
            # we can assume v is dict, because json???
            for x in v:
                yield from my_json_parse(x, prefix=k+"_")
                # yield my_json_parse(..) returns simply generator, so we need "yield from" 
        else:
            raise ValueError

def my_dict_df(dic):
    out = {} 
    for x in my_json_parse(dic):
        if out.get(x[0]):
            out[x[0]].append(x[1])
        else:
            out[x[0]] = [x[1]]

    return pd.DataFrame(
            data=list(zip_longest(*[v for _, v in out.items()])),
            columns=out.keys()
         ).fillna(method="pad")

def main():
    with open("account_summary.json","r") as f:
        d = json.loads(f.read())
    my_iter_df(d)


if __name__ == "__main__":
    main()
    #pass

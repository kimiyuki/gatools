import pandas as pd
from enum import Enum
from collections import namedtuple
from typing import NamedTuple, List, Tuple
import re

## convinience for users to pick some in many number of dimensions and metrics in google analytics
url = 'https://www.googleapis.com/analytics/v3/metadata/ga/columns?pp=1'
import requests, json
res  = requests.get(url)
out = json.loads(res.content)

def select_elements(items:List) -> Tuple:
    for item in items: 
        tp = item['attributes']['type']
        name = re.sub("ga:", '', item['id'])
        group = item['attributes']['group']
        yield (tp, name, group)

items = out['items']

DimMetExplorer = pd.DataFrame.from_records(
        select_elements(items), columns=['type', 'name', 'group'])


def create_citems(items:List) -> NamedTuple:
  """create namedtuple of Enums"""

  groups = list(set([re.sub(" ", "", x['attributes']['group']) for x in items]))
  GRP = namedtuple("GRP", groups)
  elements = []
  for group in groups:
    citems = [x['id'] for x in items 
                      if re.sub(" ", "", x['attributes']['group']) == group]    
    enum_group = Enum(group, [re.sub("ga:|\>.*","", x) for x in citems])
    elements.append(enum_group)
  return GRP(*elements)

mt = [x for x in items if x['attributes']['type']=='METRIC']
dm = [x for x in items if x['attributes']['type']=='DIMENSION']
MT = create_citems(list(mt))
DM = create_citems(dm)


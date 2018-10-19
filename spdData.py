import numpy as np
import pandas as pd
from dataclasses import dataclass
from typing import List, Any


class SpdData:    
    def __init__(self, service_spd, service_drive):
        self.service_spd = service_spd
        self.service_drive = service_drive
    
    def list_spreadsheets(self):
        """list spreadsheets of your accoujnt"""
        pass

    def _is_valid_request(self, req):
        #dimensions is not necessary in google API, though I put it
        KEYS = ['dateRanges', 'metrics', 'dimensions'] 
        if type(req) is not dict:
            raise TypeError
        if not all([x in req.keys() for x in KEYS]):
            print(f'at least {",".join(KEYS)} needed')
            raise ValueError
        return True

    def get_spreadsheet(self, id:str):
        """return spreadsheet name, id, list of sheets props"""
        res = self.service_spd.spreadsheets().get(spreadsheetId=id, ranges=[]).execute()
        sheets = [Sheet(title=x['properties']['title'], id=x['properties']['sheetId'])
                         for x in res['sheets']]
        return SpreadSheet(title=res['properties']['title'], id=id, sheets=sheets)


@dataclass 
class Cell:
    title: str
    value: Any 
    type: str

@dataclass
class Sheet:
    title: str
    id: str
    cells: List[Cell]

@dataclass
class SpreadSheet:
    title: str
    id: str
    sheets: List[Sheet]


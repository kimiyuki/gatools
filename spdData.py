import numpy as np
import pandas as pd
from dataclasses import dataclass
from typing import List, Any


class SpdData:    
    def __init__(self, service_spd, service_drive):
        self.service_spd = service_spd
        self.service_drive = service_drive
    
    def list_spreadsheets(
        self, orderBy="recency",
        q = "mimeType = 'application/vnd.google-apps.spreadsheet'",
        nextPageToken=None):
        """list spreadsheets of your accoujnt
           pageSize can be 1000 in the api"""
        results = self.service_drive.files().list(
            pageSize=1000, orderBy=orderBy, pageToken=nextPageToken, q= q,
            fields="nextPageToken, files(id, name, mimeType, modifiedTime)", 
        ).execute()
        items = results.get("files", [])
        if not items:
            print("No files found.")
        else:
            for item in items:
                item['modifiedTime'] = pd.to_datetime(item['modifiedTime'])
                yield item
        ntoken = results.get('nextPageToken')
        if ntoken:
            print('nextToken')
            yield from self.list_spreadsheets(orderBy=orderBy, nextPageToken=ntoken)

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


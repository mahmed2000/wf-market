import requests
import os, getpass, re, pickle, getpass, json

class Session():
    def __init__(self):
        self.client = requests.Session()

    def api_request(self, url='/', method='get', **kwargs):
        return json.loads(getattr(self.client, method)('https://api.warframe.market/v1' + url, **kwargs).text)




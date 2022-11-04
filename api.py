import requests
import os, getpass, re, pickle, getpass

class Session():
    def __init__(self):
        self.client = requests.Session()
    
    def set_csrf(self):
        self.client.headers['x-csrftoken'] = re.search('csrf-token\" content=\"(.*)\">', self.client.get('https://warframe.market').text).group(1)

    def api_request(self, url='/', method='get', **kwargs):
        return getattr(self.client, method)('https://api.warframe.market/v1' + url, **kwargs)

    def login(self, force = False):
        self.set_csrf()
        if os.path.exists('JWT.pkl') and not force:
            with open('JWT.pkl', 'rb') as f:
                self.client.cookies.update(pickle.load(f))
        else:
            self.api_request(url='/auth/signin', method='post', json={
                    "auth_type": "cookie",
                    "email": input('Email: '),
                    "password": getpass.getpass("Password: ")
                })
            if self.client.cookies.get('JWT'):
                with open('JWT.pkl', 'wb') as f:
                    pickle.dump(self.client.cookies. f)


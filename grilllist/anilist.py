import json
import os
import requests
import time
from . import exception, user

class Client:
    PREFIX = 'http://anilist.co/api/'
    UA = 'py/grilllist'
    REDIRECTURI = 'https://github.com/Tiefkuehlpizze/grilllist' # Placeholder or something /o\

    def __init__(self, id, secret, pin=None):
        self.id = id
        self.secret = secret
        self.access_token = None
        self.expire_time = None
        self.pin = pin
        self.refresh_token = None
        self.haslogin = False

    def hasLogin(self, noexcept=False):
        if noexcept or self.haslogin:
            return self.haslogin
        raise exception.NotAuthenticatedError("User not authentificated")

    def expired(self):
        if self.expire_time == None:
            return true
        return time.time() > self.expire_time

    def getaccesstoken(self):
        if self.access_token != None and not self.expired():
            return self.access_token
        
        url = self.PREFIX + 'auth/access_token'
        
        payload = {
            'grant_type' : 'client_credentials',
            'client_id' : self.id,
            'client_secret': self.secret,
        }
        print(self.refresh_token)
        if type(self.refresh_token) is str:
            print('refreshing token')
            payload['grant_type'] = 'refresh_token'
            payload['refresh_token'] = self.refresh_token
        elif type(self.pin) is str:
            print('authorizing')
            payload['grant_type'] = 'authorization_pin'
            payload['code'] = self.pin

        print('getaccesstoken; granttype: %s' % payload['grant_type'])
        headers = {
            'Content-Type' : 'application/x-www-form-urlencoded',
            'User-Agent' : self.UA,
        }
        start = time.time()
        response = requests.post(url, data=payload, headers=headers)
        res = response.json()
        if 'error' in res:
            raise exception.ApiError(res['error'], res['error_description'])
        self.access_token = res['access_token']
        self.expire_time = start + res['expires_in']
        self.refresh_token = res['refresh_token'] if 'refresh_token' in res else None
        self.haslogin = self.refresh_token is not None

        return self.access_token

    def getPinUri(self):
        return self.PREFIX + 'auth/authorize?grant_type=authorization_pin&client_id=%s&response_type=pin&redirect_uri=%s' % (
            self.id, self.REDIRECTURI
    )

    def setPin(self, pin):
        if type(pin) is not str:
            raise TypeError("pin is not a string")
        self.pin = pin
        self.expire_time = 0

    def checkerror(self, response):
        print(response.content)
        if response.status_code >= 400:
            raise exception.ApiError("API returned non positive statuscode", response.status_code)
        if len(response.content) > 0:
            try:
                int(response.content)
                return response
            except ValueError:
                pass
            cont = response.json()
            if 'error' in cont:
                raise self.exceptions[cont['error']](cont['error'], cont['error_description'])
        return response
                

    def get(self, path, **query):
        headers = {
            'access_token' : self.getaccesstoken(),
            'User-Agent' : self.UA,
        }

        query['access_token'] = self.getaccesstoken()
        url = self.PREFIX + path
        response = self.checkerror(requests.get(url, params=query, headers=headers))
        try:
            return response.json()
        except ValueError:
            return None
    
    def post(self, path, **query):
        if self.pin is None:
            raise NotAuthenticatedError("Action cannot be done until authentificated")
        headers = {
            'access_token' : self.getaccesstoken(),
            'User-Agent' : self.UA,
        }
        query['access_token'] = self.getaccesstoken()
        url = self.PREFIX + path

        response = self.checkerror(requests.post(url, headers=headers, data=query))
        print(response)
        if response.status_code == 200:
            return True
        else:
            return response.status_code

    def delete(self, path, **data):
        headers = {
            'access_token' : self.getaccesstoken(),
            'User-Agent' : self.UA,
        }

        query['access_token'] = self.getaccesstoken()
        url = self.PREFIX + path
        
        response = self.checkerror(requests.delete(url, headers=headers, data=data))
        return response.json()

    def sleep(self, filename='state.txt'):
        data = {
            'id' : self.id,
            'secret' : self.secret,
            'access_token' : self.access_token,
            'expire_time' : self.expire_time,
            'refresh_token' : self.refresh_token,
            'pin' : self.pin,
        }
        with open(filename, 'w') as f:
            f.write(json.dumps(data))

    @staticmethod
    def wake(filename='state.txt'):
        with open(filename, 'r') as f:
            data = json.loads(f.read())
        c = Client(data['id'], data['secret'])
        c.access_token = data['access_token']
        c.expire_time = data['expire_time']
        c.refresh_token = data['refresh_token']
        c.pin = data['pin']
        print(c.refresh_token)
        c.haslogin = c.refresh_token is not None
        return c

    @staticmethod
    def canWake(filename='state.txt'):
        return os.path.isfile(filename)
        

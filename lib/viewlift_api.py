import requests
import json
import urllib.request
import htmlement
import re
import time
from base64 import b64decode


class ViewliftAPI:
    viewliftBaseUrl = "https://prod-api.viewlift.com/"
    session = requests.Session()

    def __init__(self, plugin):
        self.plugin = plugin
        self.TOKEN = ''
        self.__user_agent = 'kodi plugin for livgolf (python)'

    def api_get(self, url, params):

        headers = {
            'connection': 'keep-alive',
            'accept': 'application/json, text/plain, */*',
            'user-agent': self.__user_agent,
            'accept-encoding': 'gzip, deflate, br',
            'authorization': self.TOKEN
        }
        response = self.session.get(url, headers=headers, params=params)
        result = None
        if response.status_code == 200 and response.headers.get('content-type') == "application/json":
            result = response.json()
        else:
            self.plugin.dialog_ok("Viewlift API Call for " +
                                  url + " did not respond 200 OK or JSON but "+str(response.status_code))
        return result

    def get_token(self):

        url = self.viewliftBaseUrl + "identity/anonymous-token"
        params = {
            'site': 'liv-golf',
        }
        result = self.api_get(url, params)
        if result is not None:
            self.TOKEN = result['authorizationToken']
            self.plugin.set_setting('token', self.TOKEN)
        return result

    @staticmethod
    def get_next_data():

        response = urllib.request.urlopen("https://www.livgolf.com/watch").read()
        htmlstr = response.decode("utf8")
        root = htmlement.fromstring(htmlstr)
        result = None
        for script in root.iterfind(".//script"):
            if script.get("id") == "__NEXT_DATA__" and script.get("type") == "application/json":
                result = json.loads(script.text, strict=False)
        return result

    def get_video_details(self, videoid):

        url = self.viewliftBaseUrl + "entitlement/video/status"
        params = {
            'id': videoid,
            'deviceType': 'web_browser',
            'contentConsumption': 'web',
        }
        result = self.api_get(url, params)
        return result

    def store_date_time(self, unix_time, is_expire):
        local_time = time.localtime(unix_time)
        store_date = time.strftime("%Y-%m-%d", local_time)
        store_time = time.strftime("%H:%M:%S", local_time)
        if is_expire:
            self.plugin.set_setting('expire_date', store_date)
            self.plugin.set_setting('expire_time', store_time)
        else:
            self.plugin.set_setting('issue_date', store_date)
            self.plugin.set_setting('issue_time', store_time)
        return True

    def store_token_settings(self):
        token = self.plugin.get_setting('token')
        print(token)
        #token += '=' * (-len(token) % 4)  # restore stripped '='s
        #token = token + b'=='
        #print(token)
        decoded_token = b64decode(token + '=' * (-len(token) % 4))
        str_decoded_token = str(decoded_token)
        val = str_decoded_token.split('{', 1)[1].split('}')[1] + '}'
        json_token = json.loads(val, strict=False)
        self.store_date_time(self.plugin.get_dict_value(json_token, 'iat'), False)
        expire_epoch = self.plugin.get_dict_value(json_token, 'exp')
        self.store_date_time(expire_epoch, True)
        self.plugin.set_setting('expire_epoch', str(expire_epoch))
        self.plugin.set_setting('ip', self.plugin.get_dict_value(json_token, 'ipaddress'))
        self.plugin.set_setting('country_code', self.plugin.get_dict_value(json_token, 'countryCode'))
        self.plugin.set_setting('postal_code', self.plugin.get_dict_value(json_token, 'postalcode'))
        return True

    def is_token_valid(self):
        expire_epoch = int(self.plugin.get_setting('expire_epoch'))
        if expire_epoch == 0:
            self.store_token_settings()
            expire_epoch = self.plugin.get_setting('expire_epoch')
        if int(time.time()) < int(expire_epoch):
            return True
        else:
            return False

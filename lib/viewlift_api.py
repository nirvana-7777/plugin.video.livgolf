import requests
import json
import urllib.request
import htmlement
import base64


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

    def store_token_settings(self):
        token = self.plugin.get_setting('token')
        decoded_token = base64.b64decode(token)
        print(decoded_token)
        return true

    def is_token_valid(self):

        expire_date = self.plugin.get_setting('expire_date')
        expire_time = self.plugin.get_setting('expire_time')
        if expire_date == '' or expire_time == '':
            store_token_settings()
        return True

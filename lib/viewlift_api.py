import requests
import base64
import json

try:
    import http.cookiejar
except ImportError:
    import cookielib
import xbmc


class ViewliftAPI:
    viewliftBaseUrl = "https://prod-api.viewlift.com/"

    def __init__(self, plugin):
        self.plugin = plugin
        self.TOKEN = ''

    def api_post(self, url, payload, referer):

        cookie_header = None
        for cookie in self.session.cookies:
            if cookie.domain == '.viewlift.com':
                cookie_header = cookie.name + "=" + cookie.value

        headers = {
            'connection': 'keep-alive',
            'accept-encoding': 'gzip, deflate, br',
        }
        response = self.session.post(url, headers=headers, data=payload)
        result = None
        if response.status_code == 200 and response.headers.get('content-type') == "application/json; charset=utf-8":
            errorcode = response.json().get("ErrorCode")
            errordesc = response.json().get("ErrorDescription")
            if errorcode != 0:
                self.plugin.dialog_ok(str(url) + " raised error " + str(errorcode) + ": " + str(errordesc))
            else:
                result = response.json().get("Result")
        else:
            self.plugin.dialog_ok("Viewlift API Call for " +
                                  url + " did not respond 200 OK or JSON but "+str(response.status_code))
        return result

    def get_token(self):

        url = self.viewliftBaseUrl + "identity/anonymous-token?&site=liv-golf"
        payload = json.dumps({})
        referer = ''
        result = self.api_post(url, payload, referer)
        print(result)
        if result is not None:
            self.TOKEN = result['authorizationToken']
            self.plugin.set_setting('token', self.TOKEN)
        return result

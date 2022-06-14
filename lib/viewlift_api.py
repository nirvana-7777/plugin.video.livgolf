import requests
#import base64
import json
import urllib.request
#from lxml import html
#import xml.etree.ElementTree as ElementTree
import htmlement

try:
    import http.cookiejar
except ImportError:
    import cookielib
import xbmc


class ViewliftAPI:
    viewliftBaseUrl = "https://prod-api.viewlift.com/"
    session = requests.Session()

    def __init__(self, plugin):
        self.plugin = plugin
        self.TOKEN = ''
        self.__user_agent = 'kodi plugin for livgolf (python)'

    def api_get(self, url, payload, referer, params):

        cookie_header = None
        for cookie in self.session.cookies:
            if cookie.domain == '.viewlift.com':
                cookie_header = cookie.name + "=" + cookie.value

        headers = {
            'connection': 'keep-alive',
            'accept': 'application/json, text/plain, */*',
            'user-agent': self.__user_agent,
            'accept-encoding': 'gzip, deflate, br',
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
        payload = json.dumps({})
        params = {
            'site': 'liv-golf',
        }
        referer = ''
        result = self.api_get(url, payload, referer, params)
        print(result)
        if result is not None:
            self.TOKEN = result['authorizationToken']
            self.plugin.set_setting('token', self.TOKEN)
        return result

    def get_videos(self):

        response = urllib.request.urlopen("https://www.livgolf.com/watch").read()
        htmlStr = response.decode("utf8")
 #       html = ElementTree.parse("https://www.livgolf.com/watch")
        root = htmlement.fromstring(htmlStr)
        title = root.find("head/title").text
        print(title)
        for script in root.iterfind(".//script"):
            print(script.get("id"))
            if script.get("id") == "__NEXT_DATA__" and script.get("type") == "application/json":
                print(script.text)
#        for elem in html.iter():
 #           print(elem.tag, elem.attrib)
        #e = html.findall('Items/Item/ItemAttributes/ListPrice/Amount')
        #content = html.xpath('//script[@id]/text()').get()
        #print(response)
        #print(content)
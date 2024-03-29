# Module: main
# Author: Nirvana
# Created on: 12.06.2022
# License: GPL v.3 https://www.gnu.org/copyleft/gpl.html
"""
Example video plugin that is compatible with Kodi 19.x "Matrix" and above
"""
import sys
from urllib.parse import urlencode, parse_qsl
import xbmc
import xbmcgui
import xbmcplugin
import xbmcaddon
#import posixpath
import time
import os
from lib.viewlift_api import ViewliftAPI
from lib.common import Common
from infotagger.listitem import ListItemInfoTag

try:
    import StorageServer
except:
    import storageserverdummy as StorageServer

_HANDLE = int(sys.argv[1])
_URL = sys.argv[0]

plugin = Common(
    addon=xbmcaddon.Addon(),
    addon_handle=_HANDLE,
    addon_url=_URL
)

cache = StorageServer.StorageServer("Viewlift", 24)
api = ViewliftAPI(plugin)
token = plugin.get_setting("token")
#username = plugin.get_setting("username")
#password = plugin.get_setting("password")
username = ''
password = ''
if token == '' or not api.is_token_valid():
    api.get_token(username, password)
else:
    api.TOKEN = token
xbmc.log("Token: " + str(api.TOKEN), level=xbmc.LOGDEBUG)


def get_url(**kwargs):
    """
    Create a URL for calling the plugin recursively from the given set of keyword arguments.
    :param kwargs: "argument=value" pairs
    :return: plugin call URL
    :rtype: str
    """
    return '{}?{}'.format(_URL, urlencode(kwargs))


def get_categories():
    """
    Get the list of video categories.
    Here you can insert some parsing code that retrieves
    the list of video categories (e.g. 'Movies', 'TV-shows', 'Documentaries' etc.)
    from some site or API.
    note:: Consider using `generator functions <https://wiki.python.org/moin/Generators>`_
        instead of returning lists.
    :return: The list of video categories
    :rtype: types.GeneratorType
    """
    categories = ["LivGolfPlus", "LivGolfPlus - Live"]
    next_data = api.get_next_data('/watch')
    if next_data is not None:
        pageprops = next_data['props']['pageProps']
        pagedata = plugin.get_dict_value(pageprops, 'pageData')
        if pagedata is not None:
            components = plugin.get_dict_value(pagedata, 'components')
            for component in components:
#                if plugin.get_dict_value(block, 'name') == filter:
                heading = plugin.get_dict_value(component, 'heading')
                if heading == "":
                    heading = plugin.get_dict_value(component, 'title')
#                    text = plugin.get_dict_value(content, 'title')
#                    if filter == 'componentIntro':
#                        teaser = plugin.get_dict_value(content, 'teaser')
#                        teaser_content = plugin.get_dict_value(teaser, 'content')
#                        for paragraph in teaser_content:
#                            paragraph_content = plugin.get_dict_value(paragraph, 'content')
#                            for text_content in paragraph_content:
#                                if plugin.get_dict_value(text_content, 'nodeType') == 'text':
#                                    text += ' - ' + plugin.get_dict_value(text_content, 'value')
                categories.append(heading)
    return categories


def list_categories():
    """
    Create the list of video categories in the Kodi interface.
    """
    # Set plugin category. It is displayed in some skins as the name
    # of the current section.
#    videos = api.get_videos()
#    print(videos)

    """
    bgimageurl = ''
    next_data = api.get_next_data('')
    if next_data is not None:
        blocks = next_data['props']['pageProps']['blocks']
        for block in blocks:
            content = plugin.get_dict_value(block, 'content')
            bgimage = plugin.get_dict_value(content, 'backgroundImage')
            if bgimage != '':
                bgimageurl = plugin.get_dict_value(bgimage, 'src')
    xbmcplugin.setPluginCategory(_HANDLE, 'Livgolf video categories')
    # Set plugin content. It allows Kodi to select appropriate views
    # for this type of content.
    xbmcplugin.setContent(_HANDLE, 'videos')
    url = get_url(action='refresh')
    list_item = xbmcgui.ListItem(label='Refresh')
    xbmcplugin.addDirectoryItem(_HANDLE, url, list_item, False)
    texts = get_categories('componentIntro')
    if bgimageurl != '':
        art['fanart'] = bgimageurl
        art['poster'] = bgimageurl
    for text in texts:
        list_item = xbmcgui.ListItem(label=text)
        list_item.setInfo('video', {'title': text,
                                    'plot': text,
                                    'genre': ['Sports', 'Golf'],
                                    'mediatype': 'video'})
        list_item.setArt(art)
        url = get_url(action='none')
        xbmcplugin.addDirectoryItem(_HANDLE, url, list_item, False)
    """

    art = {'clearart': os.path.join(xbmcaddon.Addon().getAddonInfo('path'), 'resources', 'LIVGOLF_logo.png'),
           'clearlogo': os.path.join(xbmcaddon.Addon().getAddonInfo('path'), 'resources', 'icon.png')}

    # Get video categories
    categories = get_categories()
    # Iterate through categories
    for category in categories:
        # Create a list item with a text label and a thumbnail image.
        list_item = xbmcgui.ListItem(label=category)
        list_item.setInfo('video', {'title': category,
                                    'genre': ['Sports', 'Golf'],
                                    'mediatype': 'video'})
        list_item.setArt(art)
        # Create a URL for a plugin recursive call.
        # Example: plugin://plugin.video.example/?action=listing&category=Animals
        url = get_url(action='listing', category=category)
        # is_folder = True means that this item opens a sub-list of lower level items.
        is_folder = True
        # Add our item to the Kodi virtual folder listing.
        xbmcplugin.addDirectoryItem(_HANDLE, url, list_item, is_folder)
        # Finish creating a virtual folder.
    xbmcplugin.endOfDirectory(_HANDLE)


def list_videos(category):
    """
    Create the list of playable videos in the Kodi interface.
    :param category: Category name
    :type category: str
    """
    # Set plugin category. It is displayed in some skins as the name
    # of the current section.
    xbmcplugin.setPluginCategory(_HANDLE, category)
    # Set plugin content. It allows Kodi to select appropriate views
    # for this type of content.
    xbmcplugin.setContent(_HANDLE, 'videos')
    # Get the list of videos in the category.
    # Iterate through videos.
    if (category == "LivGolfPlus") or (category == "LivGolfPlus - Live"):
        if category == "LivGolfPlus":
            path = "/"
        else:
            path = "/watch"
        videos = api.get_videos(path,0,4)
        modulecount = plugin.get_dict_value(videos, 'moduleCount')
        videos = api.get_videos(path,0,modulecount)
        modules = plugin.get_dict_value(videos, 'modules')
        for module in modules:
            if plugin.get_dict_value(module, 'contentType') == 'Video':
                contendata = plugin.get_dict_value(module, 'contentData')
                for content in contendata:
                    gist = plugin.get_dict_value(content, 'gist')
                    videoid = plugin.get_dict_value(gist, 'id')
                    metadata = {
                        'mediatype': 'video',
                        'genre': ['Sports', 'Golf']
                    }
                    li_label = plugin.get_dict_value(gist, 'title')
                    metadata['title'] = li_label
                    metadata['plot'] = plugin.get_dict_value(gist, 'description')
                    metadata['duration'] = plugin.get_dict_value(gist, 'runtime')
                    date = plugin.get_dict_value(gist, 'publishDate')
                    if date is not None:
                        metadata['aired'] = plugin.get_datetime_from_epoch_plain(date)
                    list_item = xbmcgui.ListItem(label=li_label)
                    list_item.setProperty('IsPlayable', 'true')
                    list_item.setInfo('video', metadata)
                    image = plugin.get_dict_value(gist, 'videoImageUrl')
#                    art = {'clearart': os.path.join(xbmcaddon.Addon().getAddonInfo('path'), 'resources', 'LIVGOLF_logo.png'),
#                            'clearlogo': os.path.join(xbmcaddon.Addon().getAddonInfo('path'), 'resources', 'icon.png'),
                    art = { 'poster': image,
                            'fanart': image}
                    list_item.setArt(art)
                    contentdetails = plugin.get_dict_value(content, 'contentDetails')
                    if contentdetails is not None:
                        closedcaptions = plugin.get_dict_value(contentdetails, 'closedCaptions')
                        for closedcaption in closedcaptions:
                            if plugin.get_dict_value(closedcaption, 'format') == "SRT":
                                subtitles = [plugin.get_dict_value(closedcaption, 'url')]
                                list_item.setSubtitles(subtitles)
                                list_item.addStreamInfo('audio', {'codec': 'aac', 'channels': 2, 'language': 'english'})
                                list_item.addStreamInfo('subtitle', {'language': 'english'})
                    playable = True
                    scheduled = plugin.get_dict_value(gist, 'scheduleStartDate')
                    if scheduled is not None:
                        if int(scheduled/1000) > plugin.get_time_now():
                            playable = False
                    if playable:
                        url = get_url(action='play', videoid=videoid)
                    else:
                        url = get_url(action='none')
                    is_folder = False
                    # Add our item to the Kodi virtual folder listing.
                    xbmcplugin.addDirectoryItem(_HANDLE, url, list_item, is_folder)
    else:
        next_data = api.get_next_data('/watch')
        if next_data is not None:
            pageprops = next_data['props']['pageProps']
            pagedata = plugin.get_dict_value(pageprops, 'pageData')
            if pagedata is not None:
                components = plugin.get_dict_value(pagedata, 'components')
                for component in components:
                    if plugin.get_dict_value(component, 'heading') == category or plugin.get_dict_value(component, 'title') == category:
                        videos = plugin.get_dict_value(component, 'pageArticles')
                        if videos == "":
                            videos = plugin.get_dict_value(component, 'media')
                        for video in videos:
                            if plugin.get_dict_value(video, '__typename') == 'DataVideo':
                                metadata = {
                                    'mediatype': 'video',
                                    'genre': ['Sports', 'Golf']
                                }
                                li_label = plugin.get_dict_value(video, 'videoTitle')
                                metadata['title'] = li_label
                                date = plugin.get_dict_value(video, 'videoDate')
                                if date is not None:
                                    metadata['aired'] = date
                                list_item = xbmcgui.ListItem(label=li_label)
                                list_item.setProperty('IsPlayable', 'true')
                                list_item.setInfo('video', metadata)
                                image = plugin.get_dict_value(video, 'thumbnailImageDesktop')
                                imageurl = plugin.get_dict_value(image, 'url')
#                               art = {'clearart': os.path.join(xbmcaddon.Addon().getAddonInfo('path'), 'resources',
#                                                            'LIVGOLF_logo.png'),
#                                       'clearlogo': os.path.join(xbmcaddon.Addon().getAddonInfo('path'), 'resources',
#                                                            'icon.png'),
                                art = {'poster': imageurl,
                                       'fanart': imageurl}
                                list_item.setArt(art)
                                url = get_url(action='play', videoid=plugin.get_dict_value(video, 'viewLiftId'))
                                is_folder = False
                                # Add our item to the Kodi virtual folder listing.
                                xbmcplugin.addDirectoryItem(_HANDLE, url, list_item, is_folder)
    # Add a sort method for the virtual folder items (alphabetically, ignore articles)
    # xbmcplugin.addSortMethod(_HANDLE, xbmcplugin.SORT_METHOD_LABEL_IGNORE_THE)

    # Finish creating a virtual folder.
    xbmcplugin.endOfDirectory(_HANDLE)


def play_video(videoid):
    """
    Play a video by the provided path.
    :param videoid: VideoID
    :type videoid: str
    """
    video_details = api.get_video_details(videoid)
#    videoassets = video_details['video']['streamingInfo']['videoAssets']
#    mpeg_url = ''
#    mpeg = plugin.get_dict_value(videoassets, 'mpeg')
#    if mpeg is not None:
#        bitrate = 0
#        for mp4 in mpeg:
#            if plugin.get_dict_value(mp4, 'bitrate') > bitrate:
#                bitrate = plugin.get_dict_value(mp4, 'bitrate')
#                mpeg_url = plugin.get_dict_value(mp4, 'url')
    #if mpeg_url != '':
    #    video_property = 'mpd'
    #    video_url = mpeg_url
    #else:
    if video_details is not None:
        title = video_details['video']['gist']['title']
        description = video_details['video']['gist']['description']
        image = video_details['video']['gist']['videoImageUrl']
        duration = video_details['video']['gist']['runtime']
        aired = video_details['video']['gist']['publishDate']
        language = video_details['video']['gist']['languageCode']
        isdrmenabled = video_details['video']['gist']['drmEnabled']
        aired_str = ""
        if aired is not None:
            unix_timestamp = aired / 1000
            utc_time = time.gmtime(unix_timestamp)
            local_time = time.localtime(unix_timestamp)
            aired_str = time.strftime("%Y-%m-%d %H:%M:%S", local_time)
        metadata = {
            'plot': description.replace('<br>', ''),
            'title': title.strip(),
            'genre': ['Sports', 'Golf'],
            'aired': aired_str,
            'duration': int(duration),
            'mediatype': 'tvshow',
        }
        if isdrmenabled:
            video_property = 'mpd'
            widevine = video_details['video']['streamingInfo']['videoAssets']['widevine']
            video_url = plugin.get_dict_value(widevine, 'url')
        else:
            video_property = 'hls'
            video_url = video_details['video']['streamingInfo']['videoAssets']['hlsDetail']['url']
            widevine = None
        playitem = xbmcgui.ListItem(label=title, path=video_url.strip())
        info_tag = ListItemInfoTag(playitem, 'video')
        info_tag.set_info(metadata)
        art = {'clearart': os.path.join(xbmcaddon.Addon().getAddonInfo('path'), 'resources',
                                        'LIVGOLF_logo.png'),
                'clearlogo': os.path.join(xbmcaddon.Addon().getAddonInfo('path'), 'resources',
                                     'icon.png'),
                'poster': image,
                'fanart': image,
                'thumb': image}
        playitem.setArt(art)
        stream_details = {
            'audio': [{ 'codec': 'aac',
                        'channels': 2,
                        'language': 'eng' }],
            'subtitle': [{ 'language': 'eng' }]}
        if language == "default":
            info_tag.set_stream_details(stream_details)
#       playitem.addStreamInfo('audio', {'codec': 'AAC', 'language': 'eng', 'channels': 2})
#       playitem.addStreamInfo('audio', {'codec': 'aac', 'language': 'en', 'channels': 2})
#       playitem.addStreamInfo('subtitle', {'language': 'en'})
        playitem.setProperty('inputstream', 'inputstream.adaptive')
        playitem.setProperty('inputstream.adaptive.manifest_type', video_property)
        if isdrmenabled:
            user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36'
            license_url = plugin.get_dict_value(widevine, 'licenseUrl')
            license_token = plugin.get_dict_value(widevine, 'licenseToken')
            playitem.setMimeType('application/xml+dash')
            playitem.setProperty('inputstream.adaptive.license_type', 'com.widevine.alpha')
            burl = 'https://www.livgolfplus.com'
            lic = license_url + '|User-Agent=' + user_agent + '&Referer=' + burl +'/&Origin=' + burl + '&X-Axdrm-Message=' + license_token + '&Content-Type= |R{SSM}|'
            playitem.setProperty('inputstream.adaptive.license_key', lic)
        playitem.setContentLookup(False)
        xbmcplugin.setResolvedUrl(_HANDLE, True, listitem=playitem)


def router(paramstring):
    """
    Router function that calls other functions
    depending on the provided paramstring
    :param paramstring: URL encoded plugin paramstring
    :type paramstring: str
    """
    # Parse a URL-encoded paramstring to the dictionary of
    # {<parameter>: <value>} elements
    params = dict(parse_qsl(paramstring))
    # Check the parameters passed to the plugin
    xbmc.log(("Params: " + str(params)), level=xbmc.LOGDEBUG)
    if params:
        if params['action'] == 'listing':
            # Display the list of videos in a provided category.
            list_videos(params['category'])
        elif params['action'] == 'play':
            # Play a video from a provided URL.
            try:
                videoid = params['videoid']
            except KeyError:
                videoid = None
            play_video(videoid)
        elif params['action'] == 'renew':
            api.get_token('', '')
            api.store_token_settings()
        elif params['action'] == 'refresh':
            print('Refresh hit')
            list_categories()
        elif params['action'] == 'none':
            pass
        else:
            # If the provided paramstring does not contain a supported action
            # we raise an exception. This helps to catch coding errors,
            # e.g. typos in action names.
            raise ValueError('Invalid paramstring: {}!'.format(paramstring))
    else:
        # If the plugin is called from Kodi UI without any parameters,
        # display the list of video categories
        list_categories()


if __name__ == '__main__':
    # Call the router function and pass the plugin call parameters to it.
    # We use string slicing to trim the leading '?' from the plugin call paramstring
    router(sys.argv[2][1:])

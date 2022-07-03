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
import posixpath
import time
import os
from lib.viewlift_api import ViewliftAPI
from lib.common import Common

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
if token == '' or not api.is_token_valid():
    api.get_token()
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


def get_categories(filter):
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
    categories = []
    next_data = api.get_next_data()
    if next_data is not None:
        blocks = next_data['props']['pageProps']['blocks']
        for block in blocks:
            if plugin.get_dict_value(block, 'name') == filter:
                content = plugin.get_dict_value(block, 'content')
                text = plugin.get_dict_value(content, 'title')
                if filter == 'componentIntro':
                    teaser = plugin.get_dict_value(content, 'teaser')
                    teaser_content = plugin.get_dict_value(teaser, 'content')
                    for paragraph in teaser_content:
                        paragraph_content = plugin.get_dict_value(paragraph, 'content')
                        for text_content in paragraph_content:
                            if plugin.get_dict_value(text_content, 'nodeType') == 'text':
                                text += ' - ' + plugin.get_dict_value(text_content, 'value')
                categories.append(text)
    return categories


def list_categories():
    """
    Create the list of video categories in the Kodi interface.
    """
    # Set plugin category. It is displayed in some skins as the name
    # of the current section.
    xbmcplugin.setPluginCategory(_HANDLE, 'Livgolf video categories')
    # Set plugin content. It allows Kodi to select appropriate views
    # for this type of content.
    xbmcplugin.setContent(_HANDLE, 'videos')
    texts = get_categories('componentIntro')
    art = {'thumb': os.path.join(ADDON.getAddonInfo('path'), 'resources', 'LIVGOLF_logo.png'),
           'icon': os.path.join(ADDON.getAddonInfo('path'), 'resources', 'icon.png')}
    for text in texts:
        list_item = xbmcgui.ListItem(label=text)
        list_item.setInfo('video', {'title': text,
                                    'plot': text,
                                    'genre': ['Sports', 'Golf'],
                                    'mediatype': 'video'})
        list_item.setArt(art)
        url = get_url(action='none')
        xbmcplugin.addDirectoryItem(_HANDLE, url, list_item, False)
    # Get video categories
    categories = get_categories('componentVideos')
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
    next_data = api.get_next_data()
    if next_data is not None:
        blocks = next_data['props']['pageProps']['blocks']
        for block in blocks:
            if plugin.get_dict_value(block, 'name') == 'componentVideos':
                content = plugin.get_dict_value(block, 'content')
                if plugin.get_dict_value(content, 'title') == category:
                    videos = plugin.get_dict_value(content, 'videos')
                    for video in videos:
                        if plugin.get_dict_value(video, 'componentName') == 'video':
                            metadata = {
                                'mediatype': 'video',
                                'genre': ['Sports', 'Golf']
                            }
                            li_label = plugin.get_dict_value(video, 'title')
                            eyebrow = plugin.get_dict_value(video, 'eyebrow')
                            if eyebrow is not None and eyebrow != '':
                                li_label += ' - ' + eyebrow
                            metadata['title'] = li_label
                            date = plugin.get_dict_value(video, 'date')
                            if date is not None:
                                li_label += ' (' + date + ')'
                                metadata['aired'] = date
                            list_item = xbmcgui.ListItem(label=li_label)
                            list_item.setProperty('IsPlayable', 'true')
                            list_item.setInfo('video', metadata)
                            image = video['teaserImage']['src']
                            list_item.setArt({'thumb': image,
                                              'icon': image,
                                              'fanart': image})
                            url = get_url(action='play', videoid=plugin.get_dict_value(video, 'videoId'))
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
    videoassets = video_details['video']['streamingInfo']['videoAssets']
    mpeg_url = ''
    mpeg = plugin.get_dict_value(videoassets, 'mpeg')
    if mpeg is not None:
        bitrate = 0
        for mp4 in mpeg:
            if plugin.get_dict_value(mp4, 'bitrate') > bitrate:
                bitrate = plugin.get_dict_value(mp4, 'bitrate')
                mpeg_url = plugin.get_dict_value(mp4, 'url')
    #if mpeg_url != '':
    #    video_property = 'mpd'
    #    video_url = mpeg_url
    #else:
    video_property = 'hls'
    video_url = video_details['video']['streamingInfo']['videoAssets']['hlsDetail']['url']
    title = video_details['video']['gist']['title']
    description = video_details['video']['gist']['description']
    image = video_details['video']['gist']['videoImageUrl']
    duration = video_details['video']['gist']['runtime']
    aired = video_details['video']['gist']['publishDate']
    language = video_details['video']['gist']['languageCode']
    unix_timestamp = aired / 1000
    utc_time = time.gmtime(unix_timestamp)
    local_time = time.localtime(unix_timestamp)
    aired_str = time.strftime("%Y-%m-%d %H:%M:%S", local_time)
    metadata = {
        'plot': description,
        'title': title,
        'genre': ['Sports', 'Golf'],
        'aired': aired_str,
        'duration': int(duration),
        'mediatype': 'tvshow',
    }
    playitem = xbmcgui.ListItem(label=title, path=video_url)
    playitem.setInfo('video', metadata)
    playitem.setArt({'thumb': image})
    if video_property == 'hls':
        playitem.setProperty('inputstream', 'inputstream.adaptive')
        playitem.setProperty('inputstream.adaptive.manifest_type', video_property)
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
            api.get_token()
            api.store_token_settings()
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

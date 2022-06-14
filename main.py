# Module: main
# Author: Nirvana
# Created on: 20.12.2021
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
if token == '':
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


def get_categories():
    """
    Get the list of video categories.
    Here you can insert some parsing code that retrieves
    the list of video categories (e.g. 'Movies', 'TV-shows', 'Documentaries' etc.)
    from some site or API.
    .. note:: Consider using `generator functions <https://wiki.python.org/moin/Generators>`_
        instead of returning lists.
    :return: The list of video categories
    :rtype: types.GeneratorType
    """
    categories = []
    next_data = api.get_next_data()
    if next_data is not None:
        components = next_data['props']['pageProps']['page']['fields']['components']
        for component in components:
            contenttypeid = component['sys']['contentType']['sys']['id']
            if contenttypeid == 'componentVideos':
                fields = component['fields']
                categories.append(fields['title'])
    return categories


def path_parse(path_string, *, normalize=True, module=posixpath):
    result = []
    if normalize:
        tmp = module.normpath(path_string)
    else:
        tmp = path_string
    while tmp != "/":
        (tmp, item) = module.split(tmp)
        result.insert(0, item)
    return result


def get_children(node, wanted_subcategory):
    children = None
    for child in node:
        if plugin.get_dict_value(child, 'ReferenceId') == wanted_subcategory:
            children = plugin.get_dict_value(child, 'Children')
    return children


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
    # Get video categories
    categories = get_categories()
    # Iterate through categories
    for category in categories:
        # Create a list item with a text label and a thumbnail image.
        list_item = xbmcgui.ListItem(label=category)
        list_item.setInfo('video', {'title': category,
                                    'genre': category,
                                    'mediatype': 'video'})
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
        components = next_data['props']['pageProps']['page']['fields']['components']
        for component in components:
            fields = component['fields']
            if fields['title'] == category:
                videos = fields['videos']
                for video in videos:
                    video_fields = video['fields']
                    li_label = plugin.get_dict_value(video_fields, 'title') + ' - ' + plugin.get_dict_value(video_fields, 'eyebrow')
                    list_item = xbmcgui.ListItem(label=li_label)
                    list_item.setProperty('IsPlayable', 'true')
                    metadata = {'mediatype': 'video'}
                    list_item.setInfo('video', metadata)
                    image = 'https:' + video_fields['teaserImage']['fields']['file']['url']
                    list_item.setArt({'thumb': image,
                                      'icon': image,
                                      'fanart': image})
                    url = get_url(action='play', videoid=plugin.get_dict_value(video_fields, 'videoId'))
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
    print(videoid)
    video_details = api.get_video_details(videoid)
    print(video_details)
    hls_url = video_details['video']['streamingInfo']['videoAssets']['hlsDetail']
    print(hls_url)
    playitem = xbmcgui.ListItem(path=hls_url)
    playitem.setProperty('inputstreamaddon', 'inputstream.adaptive')
    playitem.setProperty('inputstream.adaptive.manifest_type', 'hls')
    #        playitem.setMimeType('application/vnd.apple.mpegurl')
    playitem.setContentLookup(False)
    xbmcplugin.setResolvedUrl(_handle, True, playitem)

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

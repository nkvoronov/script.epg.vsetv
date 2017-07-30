# -*- coding: utf-8 -*-

import sys
import os
import xbmcaddon

sys.path.append(xbmc.translatePath(os.path.join(xbmcaddon.Addon('script.epg.vsetv').getAddonInfo('path'), 'resources', 'lib')))
import functions

if len(sys.argv) == 2:
    if sys.argv[1] == 'refresh_channels':
        functions.refresh_channels()
        xbmcaddon.Addon('script.epg.vsetv').openSettings()
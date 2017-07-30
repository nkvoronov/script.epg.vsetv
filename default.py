# -*- coding: utf-8 -*-

import sys
import os
import xbmcaddon

sys.path.append(xbmc.translatePath(os.path.join(xbmcaddon.Addon('script.epg.vsetv').getAddonInfo('path'), 'resources', 'lib')))
import functions

functions.run_update_epg()


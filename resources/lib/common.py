# -*- coding: utf-8 -*-

import os
import sys
import urllib
import urllib.request
import traceback
import xbmc
import xbmcvfs
import xbmcaddon
from xml.dom import minidom

#COMMON

host = 'http://www.vsetv.com/'
addonid = 'script.epg.vsetv'
settings_file = 'channels-settings'

is_service = False
__busy__ = 0
__common__ = sys.modules[globals()['__name__']]
input_request = False
logErorr = xbmc.LOGERROR


#BASE CLASS

class Base:

    def __init__(self):
        try:
            self._addonid = addonid
            self._addon = xbmcaddon.Addon(self._addonid)
            self._addonName = self._addon.getAddonInfo('name')
            self._addonPath = self._addon.getAddonInfo('path')
            self._debug = self._addon.getSetting('debug')
            self._settingsFile = xbmcvfs.translatePath(self._addon.getAddonInfo('profile')) + 'channels' + os.path.sep + settings_file
        except Exception as e:
            common.addLog('Base::__init__', 'ERROR: (' + repr(e) + ')', logErorr)

    def getLang(self, code):
        return self._addon.getLocalizedString(code)

    def addLog(self, source, text, level=xbmc.LOGINFO):
        if self._debug == 'false':
            return
        xbmc.log('## ' + self._addonName + ' ## ' + source + ' ## ' + text, level)
        xbmc.log(traceback.format_exc())

    def setBusy(self, state):
        global __busy__, __common__, input_request, is_service
        try:
            if not is_service:
                if state == 1:
                    __busy__ = __busy__ + 1
                else:
                    __busy__ = __busy__ - 1
                self.addLog('Base::setBusy', '__busy__ = ' + unicode(__busy__))
                if __busy__ > 0:
                    if not input_request:
                        xbmc.executebuiltin('ActivateWindow(busydialognocancel)')
                else:
                    xbmc.executebuiltin('Dialog.Close(busydialognocancel)')
        except Exception as e:
            self.addLog('Base::setBusy', 'ERROR: (' + repr(e) + ')', logErorr)

    def loadUrl(self, url):
        try:
            self.addLog('Base::loadUrl', 'enter_function')
            self.addLog('Base::loadUrl','OPEN URL: ' + url)
            headers = {
            'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3',
            'Content-Type': 'application/x-www-form-urlencoded'}
            connect = urllib.request.urlopen(urllib.request.Request(url, urllib.urlencode({}), headers))
            html = connect.read()
            connect.close()
            self.addLog('Base::loadUrl', 'exit_function')
            return html.strip()
        except Exception as e:
            self.addLog('Base::loadUrl(' + url + ')', 'ERROR: (' + repr(e) + ')', logErorr)

    def removeSpecSym(self, mstr):
        try:
            self.addLog('Base::removeSpecSym', 'enter_function')
            rstr = mstr.strip('&nbsp;')
            rstr = rstr.replace('&amp;', '&')
            rstr = rstr.replace('&quot;','"')
            rstr = rstr.replace('&lt;', '<')
            rstr = rstr.replace('&gt;', '>')
            rstr = rstr.replace('&', '&amp;')
            self.addLog('Base::removeSpecSym', 'exit_function')
            return rstr
        except Exception as e:
            self.addLog('Base::removeSpecSym', 'ERROR: (' + repr(e) + ')', logErorr)
            return vstr

    def saveXmlFile(self, filename, xmldoc):
        try:
            self.addLog('Base::saveXmlFile', 'enter_function')
            outputfile = open(filename, 'w')
            data = xmldoc.toprettyxml(encoding='utf-8')
            outputfile.write(self.removeSpecSym(data))
            outputfile.close()
            self.addLog('Base::saveXmlFile', 'exit_function')
        except Exception as e:
            self.addLog('Base::saveXmlFile', 'ERROR: (' + repr(e) + ')', logErorr)

    def getIntToTime(self, val):
        try:
            self.addLog('Base::getIntToTime', 'enter_function')
            return '{:02d}:{:02d}'.format(*divmod(int(val), 60))
            self.addLog('Base::getIntToTime', 'exit_function')
        except Exception as e:
            self.addLog('Base::getIntToTime', 'ERROR: (' + repr(e) + ')', logErorr)

    def getTimeToInt(self, val):
        try:
            self.addLog('Base::getTimeToInt', 'enter_function')
            h, m = val.split(':')
            return int(h) * 60 + int(m)
            self.addLog('Base::getTimeToInt', 'exit_function')
        except Exception as e:
            self.addLog('Base::getTimeToInt', 'ERROR: (' + repr(e) + ')', logErorr)

    def getValueFromSettings(self, id, default):
        try:
            self.addLog('Base::getValueFromSettings', 'enter_function')
            res = default
            if os.path.exists(self._settingsFile):
                with open(self._settingsFile, 'r') as rfile:
                    for line in rfile:
                        if ':' in line:
                            self.addLog('ChannelList::getValueFromSettings', line)
                            fid, fvalue = line.split(':')
                            if id == fid:
                                res = fvalue.strip('\n')
                                break
                        else:
                            pass
            self.addLog('Base::getValueFromSettings', 'RES - ' + res)
            self.addLog('Base::getValueFromSettings', 'exit_function')
            return res
        except Exception as e:
            self.addLog('Base::getValueFromSettings', 'ERROR: (' + repr(e) + ')', logErorr)

    def setValueToSettings(self, id, val):
        try:
            self.addLog('Base::setValueToSettings', 'enter_function')
            find = 0
            settings = {}
            if os.path.exists(self._settingsFile):
                with open(self._settingsFile, 'r') as rfile:
                    for line in rfile:
                        if ':' in line:
                            self.addLog('ChannelList::getValueFromSettings', line)
                            fid, fvalue = line.split(':')
                            settings[fid] = fvalue.strip('\n')
                        else:
                            pass
            settings[id] = val
            self.addLog('Base::getValueFromSettings', 'FILE - ' + self._settingsFile)
            with open(self._settingsFile, 'w') as wfile:
                for fid in sorted(settings.keys()):
                    fvalue = settings[fid]
                    if fvalue != '':
                        wfile.write('%s:%s\n' % (fid, fvalue))
            self.addLog('Base::getValueFromSettings', 'exit_function')
        except Exception as e:
            self.addLog('Base::setValueToSettings', 'ERROR: (' + repr(e) + ')', logErorr)

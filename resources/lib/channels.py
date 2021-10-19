# -*- coding: utf-8 -*-

import os
import re
import xbmc
import xbmcvfs
import xbmcaddon
from resources.lib.common import Base, logErorr, host
from xml.dom import minidom

channels_file = 'channels-list'

class Channel(Base):

    def __init__(self, index, orgName, userName='', icon='', correction=0, status=0, enable=0):
        try:
            Base.__init__(self)
            self._index = index
            self._orgName = orgName
            self._userName = userName
            self._icon = icon
            self._correction = correction
            # status : 0 - default; 1 - delete; 2 - new; 3 - update
            self._status = status
            self._enable = enable
        except Exception as e:
            self.addLog('Channel::__init__', 'ERROR: (' + repr(e) + ')', logErorr)

    def getString(self):
        try:
            self.addLog('Channel::getString', 'enter_function')
            mstr = '%s;%s;%s;%s;%s;%s;%s\n' % (str(self._index), self._orgName, self._userName, self._icon, str(self._correction), str(self._status), str(self._enable))
            self.addLog('Channel::getString', mstr)
            self.addLog('Channel::getString', 'exit_function')
            return mstr
        except Exception as e:
            self.addLog('Channel::getString', 'ERROR: (' + repr(e) + ')', logErorr)

    def getXml(self, xmldoc, node):
        try:
            self.addLog('Channel::getXml', 'enter_function')
            echannel = xmldoc.createElement('channel')
            echannel.setAttribute('id', str(self._index))
            edisplayname = xmldoc.createElement('display-name')
            if self._userName == '':
                edisplayname_text = xmldoc.createTextNode(self._orgName)
            else:
                edisplayname_text = xmldoc.createTextNode(self._userName)
            edisplayname.appendChild(edisplayname_text)
            echannel.appendChild(edisplayname)
            if self._icon != '':
                eiconlink = xmldoc.createElement('icon')
                eiconlink.setAttribute('src', self._icon)
                echannel.appendChild(eiconlink)
            node.appendChild(echannel)
            self.addLog('Channel::getXml', 'exit_function')
        except Exception as e:
            self.addLog('Channel::getXml', 'ERROR: (' + repr(e) + ')', logErorr)

class ChannelList(Base):

    def __init__(self):
        try:
            Base.__init__(self)
            #channels dir
            channelsDir = xbmcvfs.translatePath(self._addon.getAddonInfo('profile')) + 'channels'
            if not os.path.exists(channelsDir):
                os.makedirs(channelsDir)
            #channel list
            self._fileChannels = channelsDir + os.path.sep + channels_file
            self._data = []
        except Exception as e:
            self.addLog('ChannelList::__init__', 'ERROR: (' + repr(e) + ')', logErorr)

    def loadChannelsFromUrl(self):
        try:
            self.addLog('ChannelList::loadChannelsFromUrl', 'enter_function')
            udata = []
            html = self.loadUrl(host + 'channels.html')
            datalst = re.compile('<option value=channel_(.+?)>(.+?)</option>').findall(html)
            for index, oname in datalst:
                icon = host + 'pic/channel_logos/' + index + '.gif'
                chn = Channel(index, oname, oname, icon)
                chn._correction = int(self.getValueFromSettings('correct', '120'))
                udata.append(chn)
            udata = sorted(udata, key = lambda chn: int(chn._index))
            self.addLog('ChannelList::loadChannelsFromUrl', 'exit_function')
            return udata
        except Exception as e:
            self.addLog('ChannelList::loadChannelsFromUrl', 'ERROR: (' + repr(e) + ')', logErorr)

    def updateChannelsFromUrl(self):
        try:
            self.addLog('ChannelList::updateChannelsFromUrl', 'enter_function')
            ai = 0
            ui = 0
            di = 0
            udata = self.loadChannelsFromUrl()
            #update
            self._data = sorted(self._data, key = lambda chn: int(chn._index))
            #all delete
            for chn in self._data:
                chn._status = 1
            for uchn in udata:
                chn = self.findChannel(int(uchn._index))
                if chn:
                    #update
                    chn._status = 0
                    upd = 0
                    #org name
                    if chn._orgName != uchn._orgName:
                        upd = 1
                        chn._orgName = uchn._orgName
                    if chn._enable == 0:
                        #user name
                        if chn._userName != uchn._userName:
                            upd = 1
                            chn._userName = uchn._userName
                        #icon
                        if chn._icon != uchn._icon:
                            upd = 1
                            chn._icon = uchn._icon
                    if upd:
                        chn._status = 3
                        self.addLog('ChannelList::updateChannelsFromUrl', 'update channel - ' + str(uchn._index))
                        ui += 1
                else:
                    #new
                    chn = Channel(uchn._index, uchn._orgName, uchn._userName, uchn._icon)
                    chn._correction = int(self.getValueFromSettings('correct', '120'))
                    chn._status = 2
                    self._data.append(chn)
                    self.addLog('ChannelList::updateChannelsFromUrl', 'add new channel - ' + str(uchn._index))
                    ai += 1
            #delete
            for chn in self._data:
                if chn._status == 1:
                    di += 1
            del udata
            self.addLog('ChannelList::updateChannelsFromUrl', 'add - ' + str(ai) + ' upd - ' + str(ui) + ' del - ' + str(di))
            self.addLog('ChannelList::updateChannelsFromUrl', 'exit_function')
        except Exception as e:
            self.addLog('ChannelList::updateChannelsFromUrl', 'ERROR: (' + repr(e) + ')', logErorr)

    def findChannel(self, index):
        try:
            self.addLog('ChannelList::findChannel', 'enter_function')
            res = None
            for chn in self._data:
                if int(chn._index) == index:
                    res = chn
                    self.addLog('ChannelList::findChannel', 'find - ' + str(index))
                    return res
            self.addLog('ChannelList::findChannel', 'exit_function')
            return res
        except Exception as e:
            self.addLog('ChannelList::findChannel', 'ERROR: (' + repr(e) + ')', logErorr)

    def sortChannels(self):
        try:
            self.addLog('ChannelList::sortChannels', 'enter_function')
            self._sortBy = int(self.getValueFromSettings('sort_by', '0'))
            if self._sortBy == 0:
                self._data = sorted(self._data, key = lambda chn: int(chn._index))
                self.addLog('ChannelList::sortChannels', 'Sort Index')
            elif self._sortBy == 1:
                self._data = sorted(self._data, key = lambda chn: str(chn._orgName))
                self.addLog('ChannelList::sortChannels', 'Sort Org Name')
            self.addLog('ChannelList::sortChannels', 'exit_function')
        except Exception as e:
            self.addLog('ChannelList::sortChannels', 'ERROR: (' + repr(e) + ')', logErorr)

    def loadChannelsFromFile(self, all=1):
        try:
            self.addLog('ChannelList::loadChannelsFromFile', 'enter_function')
            self._data = []
            if os.path.exists(self._fileChannels):
                with open(self._fileChannels, 'r', encoding='utf-8') as cfile:
                    for line in cfile:
                        if ';' in line:
                            index, oname, uname, icon, correction, status, enable = line.split(';')
                            istatus = int(status)
                            ienable = int(enable.strip('\n'))
                            if (ienable == 1 and istatus != 1) or all == 1:
                                chn = Channel(int(index), oname, uname, icon, int(correction), istatus, ienable)
                                self._data.append(chn)
                                self.addLog('ChannelList::loadChannelsFromFile', line)
                                self.addLog('ChannelList::loadChannelsFromFile', oname.strip('"') + '(' + index.strip('"') + ')')
                        else:
                            pass
            self.addLog('ChannelList::loadChannelsFromFile', 'exit_function')
        except Exception as e:
            self.addLog('ChannelList::loadChannelsFromFile', 'ERROR: (' + repr(e) + ')', logErorr)

    def saveChannelsToFile(self):
        try:
            self.addLog('ChannelList::saveChannelsToFile', 'enter_function')
            self._data = sorted(self._data, key = lambda chn: int(chn._index))
            if os.path.exists(self._fileChannels):
                os.remove(self._fileChannels)
            with open(self._fileChannels, 'w', encoding='utf-8') as cfile:
                for chn in self._data:
                    cfile.write(chn.getString())
            self.addLog('ChannelList::saveChannelsToFile', 'exit_function')
        except Exception as e:
            self.addLog('ChannelList::saveChannelsToFile', 'ERROR: (' + repr(e) + ')', logErorr)

    def setDisabledAll(self):
        try:
            self.addLog('ChannelList::setDisabledAll', 'enter_function')
            for chn in self._data:
                if chn._enable == 1:
                    chn._enable = 0
            self.addLog('ChannelList::setDisabledAll', 'exit_function')
        except Exception as e:
            self.addLog('ChannelList::setDisabledAll', 'ERROR: (' + repr(e) + ')', logErorr)

    def updateChannelCorrection(self, correction):
        try:
            self.addLog('ChannelList::setDisabledAll', 'enter_function')
            for chn in self._data:
                if chn._enable == 1 and chn._status != 1:
                    chn._correction = correction
            self.addLog('ChannelList::setDisabledAll', 'exit_function')
        except Exception as e:
            self.addLog('ChannelList::setDisabledAll', 'ERROR: (' + repr(e) + ')', logErorr)

    def getXml(self, xmldoc, node):
        try:
            self.addLog('ChannelList::getXml', 'enter_function')
            for chn in self._data:
                chn.getXml(xmldoc, node)
            self.addLog('ChannelList::getXml', 'exit_function')
        except Exception as e:
            self.addLog('ChannelList::getXml', 'ERROR: (' + repr(e) + ')', logErorr)

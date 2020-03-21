# -*- coding: utf-8 -*-

import os
import sys
import xbmc
import xbmcaddon
import xbmcgui
import subprocess
import datetime
from common import Base, logErorr
from channels import Channel, ChannelList
from parservsetv import Parser
from editchannels import EditChannels
from xml.dom.minidom import parse

class Epg(Base):

    def __init__(self, isService=0):
        try:
            Base.__init__(self)
            self._addonMedia = xbmc.translatePath(os.path.join(os.path.join(os.path.join(os.path.join(self._addonPath, 'resources'), 'skins'), 'default'), 'media'))

            self._executeScript = self._addon.getSetting('execute_script')
            self._pathScript = self._addon.getSetting('script_path')
            self._enableService = self._addon.getSetting('enable_service')
            self._enableMonday = self._addon.getSetting('enable_monday')
            self._enableTuesday = self._addon.getSetting('enable_tuesday')
            self._enableWednesday = self._addon.getSetting('enable_wednesday')
            self._enableThursday = self._addon.getSetting('enable_thursday')
            self._enableFriday = self._addon.getSetting('enable_friday')
            self._enableSaturday = self._addon.getSetting('enable_saturday')
            self._enableSunday = self._addon.getSetting('enable_sunday')
            self._runTime = self._addon.getSetting('run_time')
            self._pathXml = xbmc.translatePath(os.path.join(self._addon.getSetting('xmltv_path'), 'xmltv.xml'))
            self._lastUpdate = self.getLastUpdate()

            self._isService = isService
            if self._isService == 1:
                if self._enableService == 'true':
                    self.serviceUpdateEpg()
            else:
                self.getParams()
                if self._action == '':
                    self.runUpdateEpg()
                else:
                    self.setAction()
        except Exception, e:
            self.addLog('Epg::__init__', 'ERROR: (' + repr(e) + ')', logErorr)

    def getLastUpdate(self):
        try:
            self.addLog('Epg::getLastUpdate', 'enter_function')
            if os.path.exists(self._pathXml):
                xmldoc = parse(self._pathXml)
                tvtag = xmldoc.getElementsByTagName('tv')
                for tv in tvtag:
                    date = tv.getAttribute('date')
                    self.addLog('Epg::getLastUpdate', 'date: ' + date, logErorr)
                    self.addLog('Epg::getLastUpdate', 'exit_function')
                    return date
            else:
                self.addLog('Epg::getLastUpdate', 'exit_function')
                return ""
        except Exception, e:
            self.addLog('Epg::getLastUpdate', 'ERROR: (' + repr(e) + ')', logErorr)
            return ""

    def getParams(self):
        try:
            self.addLog('Epg::getParams', 'enter_function')
            if len(sys.argv) > 1:
                params = dict(arg.split("=") for arg in sys.argv[ 1 ].split("&"))
            else:
                params = {}
            self.addLog('Epg::getParams', 'params: %s' % params, logErorr)
            self._action = params.get('action', '')
            self.addLog('Epg::getParams', 'exit_function')
        except Exception, e:
            self.addLog('Epg::getParams', 'ERROR: (' + repr(e) + ')', logErorr)

    def setAction(self):
        try:
            self.addLog('Epg::setAction', 'enter_function')
            if self._action == 'editchannels':
                self.editChannels()
            self.addLog('Epg::setAction', 'exit_function')
        except Exception, e:
            self.addLog('Epg::setAction', 'ERROR: (' + repr(e) + ')', logErorr)

    def editChannels(self):
        try:
            self.addLog('Epg::editChannels', 'enter_function')
            ui = EditChannels('script-vsetv-editchannels-main.xml', self._addonPath, 'default', None)
            del ui
            self.addLog('Epg::editChannels', 'exit_function')
        except Exception, e:
            self.addLog('Epg::editChannels', 'ERROR: (' + repr(e) + ')', logErorr)

    def setNotify(self, title, message, icon='icon', time=5000):
        try:
            self.addLog('Epg::setNotify', 'enter_function')
            picon = xbmc.translatePath(os.path.join(self._addonMedia, icon + '.png'))
            xbmcgui.Dialog().notification(title, message, picon, time)
            self.addLog('Epg::setNotify', 'exit_function')
        except Exception, e:
            self.addLog('Epg::setNotify', 'ERROR: (' + repr(e) + ')', logErorr)

    def Execute(self, command_line, get_result=0):
        try:
            self.addLog('Epg::Execute', 'enter_function')
            self.addLog('Epg::Execute::command', command_line)
            if get_result == 0:
                process = subprocess.Popen(command_line, shell=True, close_fds=True)
                process.wait()
            else:
                result = ''
                process = subprocess.Popen(command_line, shell=True, close_fds=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                process.wait()
                for line in process.stdout.readlines():
                    result = result + line
                return result
            self.addLog('Epg::Execute', 'exit_function')
        except Exception, e:
            self.addLog('Epg::Execute', 'ERROR: (' + repr(e) + ')', logErorr)

    def saveXmltv(self):
        try:
            self.addLog('Epg::saveXmltv', 'enter_function')
            self.setNotify(self._addonName, self.getLang(33001), 'vsetv-info')
            progressDialog = xbmcgui.DialogProgressBG()
            progressDialog.create(self.getLang(33004), '')
            prs = Parser(progressDialog)
            prs.getContent()
            prs.saveXml()
            progressDialog.close()
            self.setNotify(self._addonName, self.getLang(33002), 'vsetv-info')
            if self._executeScript == 'true':
                self.addLog('Epg::saveXmltv', 'execute script - ' + self._pathScript)
                self.Execute(self._pathScript)
            self.addLog('Epg::saveXmltv', 'exit_function')
        except Exception, e:
            self.setNotify(self._addonName, self.getLang(33003), 'vsetv-error')
            self.addLog('Epg::saveXmltv', 'ERROR: (' + repr(e) + ')', logErorr)

    def serviceUpdateEpg(self):
        try:
            self.addLog('Epg::serviceUpdateEpg', 'enter_function')
            week_day = datetime.date.today().isoweekday()
            cur_time = datetime.datetime.now().strftime('%H:%M')
            cur_date = datetime.datetime.now().strftime('%Y%m%d')
            if week_day == 1:
                enable_upd_week = self._enableMonday == 'true'
            elif week_day == 2:
                enable_upd_week = self._enableTuesday == 'true'
            elif week_day == 3:
                enable_upd_week = self._enableWednesday == 'true'
            elif week_day == 4:
                enable_upd_week = self._enableThursday == 'true'
            elif week_day == 5:
                enable_upd_week = self._enableFriday == 'true'
            elif week_day == 6:
                enable_upd_week = self._enableSaturday == 'true'
            elif week_day == 7:
                enable_upd_week = self._enableSunday == 'true'
            else:
                enable_upd_week = False
            enable_upd_time = self._runTime <= cur_time
            enable_upd_day = self._lastUpdate != cur_date
            if enable_upd_time and enable_upd_week and enable_upd_day:
                self.saveXmltv()
            self.addLog('Epg::serviceUpdateEpg', 'exit_function')
        except Exception, e:
            self.addLog('Epg::serviceUpdateEpg', 'ERROR: (' + repr(e) + ')', logErorr)

    def runUpdateEpg(self):
        try:
            self.addLog('Epg::runUpdateEpg', 'enter_function')
            dialog = xbmcgui.Dialog()
            if dialog.yesno(self._addonName, self.getLang(33000)):
                self.saveXmltv()
            self.addLog('Epg::runUpdateEpg', 'exit_function')
        except Exception, e:
            self.addLog('Epg::runUpdateEpg', 'ERROR: (' + repr(e) + ')', logErorr)

# -*- coding: utf-8 -*-

import os
import sys
import xbmc
import xbmcaddon
import xbmcgui
from common import Base, logErorr
from channels import Channel, ChannelList
from channeledit import ChannelEdit

class EditChannels(Base, xbmcgui.WindowXMLDialog):

    def __init__(self, *args, **kwargs):
        try:
            Base.__init__(self)
            xbmcgui.WindowXMLDialog.__init__(self, *args, **kwargs)
            self._sortBy = int(self.getValueFromSettings('sort_by', '0'))
            self._correction = int(self.getValueFromSettings('correct', '120'))
            self.doModal()
        except Exception, e:
            self.addLog('EditChannels::__init__', 'ERROR: (' + repr(e) + ')', logErorr)

    def onInit(self):
        try:
            self.addLog('EditChannels::onInit', 'enter_function')
            self.defineControls()
            self.showDialog()
            self.addLog('EditChannels::onInit', 'exit_function')
        except Exception, e:
            self.addLog('EditChannels::onInit', 'ERROR: (' + repr(e) + ')', logErorr)

    def defineControls(self):
        try:
            self.addLog('EditChannels::defineControls', 'enter_function')
            #actions
            self._action_cancel_dialog = ( 9, 10, 92, 216, 247, 257, 275, 61467, 61448 )
            item1 = self.getLang(32044)
            item2 = self.getLang(32045)
            self._list_sort_by = [item1, item2]
            #control ids
            self._control_heading_label_id = 1
            self._control_achannels_update_button_id = 20
            self._control_achannels_sortby_button_id = 21
            self._control_achannels_list_id = 22
            self._control_schannels_clear_button_id = 24
            self._control_schannels_correction_button_id = 25
            self._control_schannels_list_id = 26
            self._control_save_button_id = 28
            self._control_cancel_button_id = 29
            #controls
            self._heading_label = self.getControl(self._control_heading_label_id)
            self._achannels_update_button = self.getControl(self._control_achannels_update_button_id)
            self._achannels_sortby_button = self.getControl(self._control_achannels_sortby_button_id)
            self._achannels_list = self.getControl(self._control_achannels_list_id)
            self._schannels_clear_button = self.getControl(self._control_schannels_clear_button_id)
            self._schannels_correction_button = self.getControl(self._control_schannels_correction_button_id)
            self._schannels_list = self.getControl(self._control_schannels_list_id)
            self._save_button = self.getControl(self._control_save_button_id)
            self._cancel_button = self.getControl(self._control_cancel_button_id)
            #init
            self._channellist = ChannelList()
            self._channellist.loadChannelsFromFile()
            self._channellist.sortChannels()
            self.addLog('EditChannels::defineControls', 'exit_function')
        except Exception, e:
            self.addLog('EditChannels::defineControls', 'ERROR: (' + repr(e) + ')', logErorr)

    def showDialog(self):
        try:
            self.addLog('EditChannels::showDialog', 'enter_function')
            self._heading_label.setLabel(self.getLang(32040))
            self._achannels_update_button.setLabel(self.getLang(32041))
            self._achannels_sortby_button.setLabel(self.getLang(32043))
            self._achannels_sortby_button.setLabel(label2=self._list_sort_by[self._sortBy])
            self._schannels_clear_button.setLabel(self.getLang(32046))
            self._schannels_correction_button.setLabel(self.getLang(32048))
            self._schannels_correction_button.setLabel(label2=self.getIntToTime(self._correction))
            self._save_button.setLabel(self.getLang(32049))
            self._cancel_button.setLabel(self.getLang(32050))
            #init
            self.updateChannelsList()
            self.setFocus(self._achannels_update_button)
            self.addLog('EditChannels::showDialog', 'exit_function')
        except Exception, e:
            self.addLog('EditChannels::showDialog', 'ERROR: (' + repr(e) + ')', logErorr)

    def onClick(self, controlId):
        try:
            self.addLog('EditChannels::onClick', 'enter_function')
            #update available channels
            if controlId == self._control_achannels_update_button_id:
                self.updateAvailableChannels()
            #sort by
            if controlId == self._control_achannels_sortby_button_id:
                self.changeSortBy()
            #available channels list
            elif controlId == self._control_achannels_list_id:
                self.setAvailableListItem()
            #clear selected channels
            elif controlId == self._control_schannels_clear_button_id:
                self.clearSelectedChannels()
            #correction
            elif controlId == self._control_schannels_correction_button_id:
                self.changeCorrection()
            #selected channels list
            elif controlId == self._control_schannels_list_id:
                self.setSelectedListItem()
            #save channels
            elif controlId == self._control_save_button_id:
                self.saveSelectedChannels()
                self.closeDialog()
            #cancel dialog
            elif controlId == self._control_cancel_button_id:
                self.closeDialog()
            self.addLog('EditChannels::onClick', 'exit_function')
        except Exception, e:
            self.addLog('EditChannels::onClick', 'ERROR: (' + repr(e) + ')', logErorr)

    def onAction(self, action):
        try:
            self.addLog('EditChannels::onAction', 'enter_function')
            if action in self._action_cancel_dialog:
                self.closeDialog()
            self.addLog('EditChannels::onAction', 'exit_function')
        except Exception, e:
            self.addLog('EditChannels::onAction', 'ERROR: (' + repr(e) + ')', logErorr)

    def updateChannelsList(self, isClear=0):
        try:
            self.addLog('EditChannels::updateChannelsList', 'enter_function')
            if isClear:
                self._achannels_list.reset()
                self._schannels_list.reset()
            a = 0
            s = 0
            for chn in self._channellist._data:
                if chn._status != 1:
                    if chn._enable:
                        Item = xbmcgui.ListItem(chn._userName)
                        Item.setLabel2('[COLOR selected]' + str(chn._index) + '[/COLOR] - ' + chn._orgName + '[COLOR blue] (' + self.getIntToTime(chn._correction) + ')[/COLOR]')
                        Item.setIconImage(chn._icon)
                        Item.setProperty('index', str(chn._index))
                        self._schannels_list.addItem(Item)
                        s += 1
                    else:
                        Item = xbmcgui.ListItem(chn._userName)
                        Item.setLabel2('[COLOR selected]' + str(chn._index) + '[/COLOR] - ' + chn._orgName)
                        Item.setIconImage(chn._icon)
                        Item.setProperty('index', str(chn._index))
                        self._achannels_list.addItem(Item)
                        a += 1
            self._achannels_update_button.setLabel(label2='[COLOR selected]' + self.getLang(32042) + str(a) + '[/COLOR]')
            self._schannels_clear_button.setLabel(label2='[COLOR selected]' + self.getLang(32047) + str(s) + '[/COLOR]')
            self.addLog('EditChannels::updateChannelsList', 'exit_function')
        except Exception, e:
            self.addLog('EditChannels::updateChannelsList', 'ERROR: (' + repr(e) + ')', logErorr)

    def changeSortBy(self):
        try:
            self.addLog('EditChannels::changeSortBy', 'enter_function')
            dialog = xbmcgui.Dialog()
            res = dialog.select(self.getLang(32043), self._list_sort_by)
            self.addLog('EditChannels::changeSortBy', 'RES - ' + str(res))
            if res != self._sortBy and res >= 0:
                self._achannels_sortby_button.setLabel(label2=self._list_sort_by[res])
                self._sortBy = res
                self.setValueToSettings('sort_by', str(res))
                self._channellist.sortChannels()
                self.updateChannelsList(1)
            self.addLog('EditChannels::changeSortBy', 'exit_function')
        except Exception, e:
            self.addLog('EditChannels::changeSortBy', 'ERROR: (' + repr(e) + ')', logErorr)

    def setAvailableListItem(self):
        try:
            self.addLog('EditChannels::selectAvailableListItem', 'enter_function')
            selItem = self._achannels_list.getSelectedItem()
            selPos = self._achannels_list.getSelectedPosition()
            index = int(selItem.getProperty('index'))
            chn = self._channellist.findChannel(index)
            if chn:
                if selPos != 0:
                    selPos = selPos -1
                chn._enable = 1
                self.updateChannelsList(1)
                self._achannels_list.selectItem(selPos)
            self.addLog('EditChannels::selectAvailableListItem', 'exit_function')
        except Exception, e:
            self.addLog('EditChannels::selectAvailableListItem', 'ERROR: (' + repr(e) + ')', logErorr)

    def updateAvailableChannels(self):
        try:
            self.addLog('EditChannels::updateAvailableChannels', 'enter_function')
            self.setBusy(1)
            self._channellist.updateChannelsFromUrl()
            self._channellist.saveChannelsToFile()
            self._channellist.loadChannelsFromFile()
            self._channellist.sortChannels()
            self.updateChannelsList(1)
            self.setBusy(0)
            self.addLog('EditChannels::updateAvailableChannels', 'exit_function')
        except Exception, e:
            self.setBusy(0)
            self.addLog('EditChannels::updateAvailableChannels', 'ERROR: (' + repr(e) + ')', logErorr)

    def clearSelectedChannels(self):
        try:
            self.addLog('EditChannels::clearSelectedChannels', 'enter_function')
            self._channellist.setDisabledAll()
            self.updateChannelsList(1)
            self.addLog('EditChannels::clearSelectedChannels', 'exit_function')
        except Exception, e:
            self.addLog('EditChannels::clearSelectedChannels', 'ERROR: (' + repr(e) + ')', logErorr)

    def changeCorrection(self):
        try:
            self.addLog('EditChannels::changeCorrection', 'enter_function')
            dialog = xbmcgui.Dialog()
            ctm = self.getIntToTime(self._correction)
            res = dialog.numeric(2, self.getLang(32048), ctm)
            self.addLog('EditChannels::changeCorrection', 'RES - ' + res)
            if res != ctm and res != '':
                self._schannels_correction_button.setLabel(label2=res)
                self._correction = self.getTimeToInt(res)
                self.setValueToSettings('correct', str(self._correction))
                self._channellist.updateChannelCorrection(self._correction)
                self.updateChannelsList(1)
            self.addLog('EditChannels::changeCorrection', 'exit_function')
        except Exception, e:
            self.addLog('EditChannels::changeCorrection', 'ERROR: (' + repr(e) + ')', logErorr)

    def setSelectedListItem(self):
        try:
            self.addLog('EditChannels::setSelectedListItem', 'enter_function')
            selItem = self._schannels_list.getSelectedItem()
            selPos = self._schannels_list.getSelectedPosition()
            index = int(selItem.getProperty('index'))
            chn = self._channellist.findChannel(index)
            if chn:
                ui = ChannelEdit('script-vsetv-editchannels-channel.xml', self._addonPath, 'default', None)
                ui.getEditData(chn)
                ui.doModal()
                if ui._result == 1:
                    ui.setEditData(chn)
                elif ui._result == 2:
                    if selPos != 0:
                        selPos = selPos -1
                    chn._enable = 0
                #del ui
                self.updateChannelsList(1)
                self._schannels_list.selectItem(selPos)
            self.addLog('EditChannels::setSelectedListItem', 'exit_function')
        except Exception, e:
            self.addLog('EditChannels::setSelectedListItem', 'ERROR: (' + repr(e) + ')', logErorr)

    def saveSelectedChannels(self):
        try:
            self.addLog('EditChannels::saveSelectedChannels', 'enter_function')
            self._channellist.saveChannelsToFile()
            self.addLog('EditChannels::saveSelectedChannels', 'exit_function')
        except Exception, e:
            self.addLog('EditChannels::saveSelectedChannels', 'ERROR: (' + repr(e) + ')', logErorr)

    def closeDialog(self):
        try:
            self.addLog('EditChannels::closeDialog', 'enter_function')
            self.close()
            self.addLog('EditChannels::closeDialog', 'exit_function')
        except Exception, e:
            self.addLog('EditChannels::closeDialog', 'ERROR: (' + repr(e) + ')', logErorr)



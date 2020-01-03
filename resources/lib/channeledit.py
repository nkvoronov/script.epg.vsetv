# -*- coding: utf-8 -*-

import os
import sys
import xbmc
import xbmcaddon
import xbmcgui
from resources.lib.common import Base, logErorr
from resources.lib.channels import Channel, ChannelList

class ChannelEdit(Base, xbmcgui.WindowXMLDialog):

    def __init__(self, *args, **kwargs):
        try:
            Base.__init__(self)
            xbmcgui.WindowXMLDialog.__init__(self, *args, **kwargs)
            self._orgName = ''
            self._userName = ''
            self._icon = ''
            self._correction = 120
            self._result = 0
        except Exception as e:
            self.addLog('ChannelEdit::__init__', 'ERROR: (' + repr(e) + ')', logErorr)

    def onInit(self):
        try:
            self.addLog('ChannelEdit::onInit', 'enter_function')
            self.defineControls()
            self.showDialog()
            self.addLog('ChannelEdit::onInit', 'exit_function')
        except Exception as e:
            self.addLog('ChannelEdit::onInit', 'ERROR: (' + repr(e) + ')', logErorr)

    def defineControls(self):
        try:
            self.addLog('ChannelEdit::defineControls', 'enter_function')
            #actions
            self._action_cancel_dialog = ( 9, 10, 92, 216, 247, 257, 275, 61467, 61448 )
            #control ids
            self._control_heading_label_id = 1
            self._control_org_name_button_id = 30
            self._control_user_name_button_id = 31
            self._control_icon_button_id = 32
            self._control_correct_button_id = 33
            self._control_delete_button_id = 34
            self._control_ok_button_id = 35
            self._control_cancel_button_id = 36
            #controls
            self._heading_label = self.getControl(self._control_heading_label_id)
            self._org_name_button = self.getControl(self._control_org_name_button_id)
            self._user_name_button = self.getControl(self._control_user_name_button_id)
            self._icon_button = self.getControl(self._control_icon_button_id)
            self._correct_button = self.getControl(self._control_correct_button_id)
            self._delete_button = self.getControl(self._control_delete_button_id)
            self._ok_button = self.getControl(self._control_ok_button_id)
            self._cancel_button = self.getControl(self._control_cancel_button_id)
            self.addLog('ChannelEdit::defineControls', 'exit_function')
        except Exception as e:
            self.addLog('ChannelEdit::defineControls', 'ERROR: (' + repr(e) + ')', logErorr)

    def showDialog(self):
        try:
            self.addLog('ChannelEdit::showDialog', 'enter_function')
            self._heading_label.setLabel(self.getLang(32056))
            self._org_name_button.setLabel(self.getLang(32051))
            self._org_name_button.setLabel(label2=self._orgName)
            self._user_name_button.setLabel(self.getLang(32052))
            self._user_name_button.setLabel(label2=self._userName)
            self._icon_button.setLabel(self.getLang(32053))
            self._icon_button.setLabel(label2=self._icon)
            self._correct_button.setLabel(self.getLang(32048))
            self._correct_button.setLabel(label2=self.getIntToTime(self._correction))
            self._delete_button.setLabel(self.getLang(32055))
            self._ok_button.setLabel(self.getLang(32054))
            self._cancel_button.setLabel(self.getLang(32050))
            self.setFocus(self._user_name_button)
            self.addLog('ChannelEdit::showDialog', 'exit_function')
        except Exception as e:
            self.addLog('ChannelEdit::showDialog', 'ERROR: (' + repr(e) + ')', logErorr)

    def onClick(self, controlId):
        try:
            self.addLog('ChannelEdit::onClick', 'enter_function')
            #name
            if controlId == self._control_user_name_button_id:
                self.editName()
            #icon
            elif controlId == self._control_icon_button_id:
                self.editIcon()
            #correction
            elif controlId == self._control_correct_button_id:
                self.editCorrect()
            #delete
            elif controlId == self._control_delete_button_id:
                self._result = 2
                self.closeDialog()
            #ok dialog
            elif controlId == self._control_ok_button_id:
                self._result = 1
                self.closeDialog()
            #cancel dialog
            elif controlId == self._control_cancel_button_id:
                self.closeDialog()
            self.addLog('ChannelEdit::onClick', 'exit_function')
        except Exception as e:
            self.addLog('ChannelEdit::onClick', 'ERROR: (' + repr(e) + ')', logErorr)

    def onAction(self, action):
        try:
            self.addLog('ChannelEdits::onAction', 'enter_function')
            if action in self._action_cancel_dialog:
                self.closeDialog()
            self.addLog('ChannelEdit::onAction', 'exit_function')
        except Exception as e:
            self.addLog('ChannelEdit::onAction', 'ERROR: (' + repr(e) + ')', logErorr)

    def getEditData(self, chn):
        try:
            self.addLog('ChannelEdits::getEditData', 'enter_function')
            self._orgName = chn._orgName
            self._userName = chn._userName
            self._icon = chn._icon
            self._correction = chn._correction
            self.addLog('ChannelEdit::getEditData', 'exit_function')
        except Exception as e:
            self.addLog('ChannelEdit::getEditData', 'ERROR: (' + repr(e) + ')', logErorr)

    def setEditData(self, chn):
        try:
            self.addLog('ChannelEdits::setEditData', 'enter_function')
            chn._userName = self._userName
            chn._icon = self._icon
            chn._correction = self._correction
            self.addLog('ChannelEdit::setEditData', 'exit_function')
        except Exception as e:
            self.addLog('ChannelEdit::setEditData', 'ERROR: (' + repr(e) + ')', logErorr)

    def editName(self):
        try:
            self.addLog('ChannelEdit::editName', 'enter_function')
            dialog = xbmcgui.Dialog()
            res = dialog.input(self.getLang(32052), self._userName)
            if res != self._userName and res != '':
                self._user_name_button.setLabel(label2=res)
                self._userName = res
            self.addLog('ChannelEdit::editName', 'exit_function')
        except Exception as e:
            self.addLog('ChannelEdit::editName', 'ERROR: (' + repr(e) + ')', logErorr)

    def editIcon(self):
        try:
            self.addLog('ChannelEdit::editIcon', 'enter_function')
            dialog = xbmcgui.Dialog()
            res = dialog.browse(2, self.getLang(32053), 'pictures', '', False, False, self._icon)
            if res != self._icon and res != '':
                self._icon_button.setLabel(label2=res)
                self._icon = res
            self.addLog('ChannelEdit::editIcon', 'exit_function')
        except Exception as e:
            self.addLog('ChannelEdit::editIcon', 'ERROR: (' + repr(e) + ')', logErorr)

    def editCorrect(self):
        try:
            self.addLog('ChannelEdit::editCorrect', 'enter_function')
            dialog = xbmcgui.Dialog()
            ctm = self.getIntToTime(self._correction)
            res = dialog.numeric(2, self.getLang(32048), ctm)
            self.addLog('ChannelEdit::editCorrect', 'RES - ' + res)
            if res != ctm and res != '':
                self._correct_button.setLabel(label2=res)
                self._correction = self.getTimeToInt(res)
            self.addLog('ChannelEdit::editCorrect', 'exit_function')
        except Exception as e:
            self.addLog('ChannelEdit::editCorrect', 'ERROR: (' + repr(e) + ')', logErorr)

    def closeDialog(self):
        try:
            self.addLog('ChannelEdit::closeDialog', 'enter_function')
            self.close()
            self.addLog('ChannelEdit::closeDialog', 'exit_function')
        except Exception as e:
            self.addLog('ChannelEdit::closeDialog', 'ERROR: (' + repr(e) + ')', logErorr)


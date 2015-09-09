# -*- coding: utf-8 -*-

import common
import shutil
import xmlpp
from xml.dom import minidom

class settings:
    __slots__ = ('SettingsFile')

    def __init__(self):
        try:
            self.SettingsFile = common.__settings_xml__
        except Exception, e:
            common.dbg_log('settings::__init__', 'ERROR: (' + repr(e) + ')', common.logErorr)
            
    def backup(self):
        try:
            common.dbg_log('settings::backup', 'enter_function')
            with open(self.SettingsFile + '_orig') as f: pass
            common.dbg_log('settings::backup', 'exit_function')
        except IOError as e:
            common.dbg_log('settings::backup', 'ERROR: (' + repr(e) + ')', common.logErorr)
            shutil.copyfile(self.SettingsFile, self.SettingsFile + '_orig')
            
    def restore(self):
        try:
            common.dbg_log('settings::restore', 'enter_function')
            shutil.copyfile(self.SettingsFile + '_orig', self.SettingsFile)
            common.dbg_log('settings::restore', 'exit_function')
        except IOError as e:
            common.dbg_log('settings::restore', 'ERROR: (' + repr(e) + ')', common.logErorr)
            
    def parse(self):
        try:
            common.dbg_log('settings::parse', 'enter_function')
            xmldoc = minidom.parse(self.SettingsFile)
            category = xmldoc.getElementsByTagName('category')
            common.dbg_log('settings::parse', 'exit_function')
            return xmldoc
        except Exception, e:
            common.dbg_log('settings::parse', 'ERROR: (' + repr(e) + ')', common.logErorr)
            return None
            
    def save(self, vxmldoc):
        try:
            common.dbg_log('settings::save', 'enter_function')
            outputfile = open(self.SettingsFile, 'w')
            xmlpp.pprint(vxmldoc.toxml('utf-8'), output = outputfile, indent=4)
            outputfile.close()
            common.dbg_log('settings::save', 'exit_function')
        except Exception, e:
            common.dbg_log('settings::save', 'ERROR: (' + repr(e) + ')', common.logErorr)
            self.restore()

    def remove_old_channels(self, vxmldoc):
        try:
            common.dbg_log('settings::remove_old_channels', 'enter_function')
            category = vxmldoc.getElementsByTagName('category')
            for node_cat in category:
                setting = node_cat.getElementsByTagName('setting')
                for node_set in setting :
                    if 'id' in node_set.attributes.keys() and not node_set.getAttribute('id').find('channel_'):
                        node_set.parentNode.removeChild(node_set)
            common.dbg_log('settings::remove_old_channels', 'exit_function')
        except Exception, e:
            common.dbg_log('settings::remove_old_channels', 'ERROR: (' + repr(e) + ')', common.logErorr)
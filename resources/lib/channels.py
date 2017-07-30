# -*- coding: utf-8 -*-

import re
import common
import addonsettings

class channel:
    __slots__ = ('Index', 'OName', 'UName', 'Icon', 'Correction')

    def __init__(self, vIndex, vOName, vUName='', vIcon='', vCorrection=120):
        try:
            self.Index = vIndex
            self.OName = vOName
            self.UName = vUName
            self.Icon = vIcon
            self.Correction = vCorrection
        except Exception, e:
            common.dbg_log('channel::__init__', 'ERROR: (' + repr(e) + ')', common.logErorr)

    def get_xml(self, vxmldoc, vnode):
        try:
            common.dbg_log('channel::get_xml', 'enter_function')
            echannel = vxmldoc.createElement("channel")
            echannel.setAttribute("id", self.Index)
            edisplayname = vxmldoc.createElement("display-name")
            edisplayname.setAttribute("lang", 'ru')
            if self.UName == '':
                edisplayname_text = vxmldoc.createTextNode(self.OName.decode('utf-8'))
            else:
                edisplayname_text = vxmldoc.createTextNode(self.UName.decode('utf-8'))
            edisplayname.appendChild(edisplayname_text) 
            echannel.appendChild(edisplayname)
            if self.Icon != '':
                eiconlink = vxmldoc.createElement("icon")
                eiconlink.setAttribute("src", self.Icon)
                echannel.appendChild(eiconlink)
            vnode.appendChild(echannel)
            common.dbg_log('channel::get_xml', 'exit_function')
        except Exception, e:
            common.dbg_log('channel::get_xml', 'ERROR: (' + repr(e) + ')', common.logErorr)

class channel_list:
    __slots__ = ('Data')

    def __init__(self):
        try:
            self.Data = []
        except Exception, e:
            common.dbg_log('channel_list::__init__', 'ERROR: (' + repr(e) + ')', common.logErorr)

    def load_channels_from_net(self):
        try:
            common.dbg_log('channel_list::load_channel_from_net', 'enter_function')
            self.Data = []
            html = common.load_url(common.host+'channels.html')
            html = html.decode('windows-1251').encode('utf-8')
            datalst = re.compile('<option value=channel_(.+?)>(.+?)</option>').findall(html)
            for index,oname in datalst:
                if common.lang == 'ru':
                    flag = oname.find('(на укр.)') == -1
                else:
                    flag = oname.find('(на укр.)') != -1
                if flag:
                    icon = common.host + 'pic/channel_logos/' + index + '.gif'
                    chn = channel(index, oname.decode('utf-8'), oname.decode('utf-8'), icon)
                    self.Data.append(chn)
            if common.sort_by_index == 'true':
                self.Data.sort(key = lambda x: int(x.Index))
            common.dbg_log('channel_list::load_channel_from_net', 'exit_function')
        except Exception, e:
            common.dbg_log('channel_list::load_channel_from_net', 'ERROR: (' + repr(e) + ')', common.logErorr)

    def load_channels_from_settings(self):
        try:
            common.dbg_log('channel_list::load_channels_from_settings', 'enter_function')
            self.Data = []
            set = addonsettings.settingaddon()
            xmldoc = set.parse()
            if xmldoc != None:
                category = xmldoc.getElementsByTagName('category')
                for node_cat in category:
                    setting = node_cat.getElementsByTagName('setting')
                    for node_set in setting :
                        if 'id' in node_set.attributes.keys() and not node_set.getAttribute('id').find('channel_sep_'):
                            offset = len('channel_sep_')
                            index = node_set.getAttribute('id')[offset:]
                            enabled = common.__addon__.getSetting('channel_enable_'+index)
                            if enabled == 'true':
                                oname = node_set.getAttribute('label')
                                uname = common.__addon__.getSetting('channel_name_'+index)
                                icon = common.__addon__.getSetting('channel_icon_'+index)
                                chn = channel(index, oname, uname, icon, common.correction)
                                self.Data.append(chn)
                                common.dbg_log('channel_list::load_channels_from_settings', oname.encode('utf-8') + '(' + index + ')')
            common.dbg_log('channel_list::load_channels_from_settings', 'exit_function')
        except Exception, e:
            common.dbg_log('channel_list::load_channels_from_settings', 'ERROR: (' + repr(e) + ')', common.logErorr)

    def save_channels_to_settings(self, vxmldoc):
        try:
            common.dbg_log('channel_list::save_channels_to_settings', 'enter_function')
            category = vxmldoc.getElementsByTagName('category')
            for node_cat in category:
                setting = node_cat.getElementsByTagName('setting')
                for node_set in setting :
                    if 'label' in node_set.attributes.keys() and '32011' in node_set.getAttribute('label'):
                        for channel in self.Data:
                            node1 = vxmldoc.createElement("setting")
                            node1.setAttribute("id", 'channel_sep_' + channel.Index)
                            node1.setAttribute("label", channel.OName)
                            node1.setAttribute("type", 'lsep')
                            node_cat.appendChild(node1)
                            node2 = vxmldoc.createElement("setting")
                            node2.setAttribute("id", 'channel_name_' + channel.Index)
                            node2.setAttribute("label", '32013')
                            node2.setAttribute("type", 'text')
                            node2.setAttribute("default", channel.OName)
                            node_cat.appendChild(node2)
                            node3 = vxmldoc.createElement("setting")
                            node3.setAttribute("id", 'channel_icon_' + channel.Index)
                            node3.setAttribute("label", '32014')
                            node3.setAttribute("type", 'text')
                            node3.setAttribute("default", channel.Icon)
                            node_cat.appendChild(node3)
                            node4 = vxmldoc.createElement("setting")
                            node4.setAttribute("id", 'channel_enable_' + channel.Index)
                            node4.setAttribute("label", '32015')
                            node4.setAttribute("type", 'bool')
                            node4.setAttribute("default", 'false')
                            node_cat.appendChild(node4)
            common.dbg_log('channel_list::save_channels_to_settings', 'exit_function')
        except Exception, e:
            common.dbg_log('channel_list::save_channels_to_settings', 'ERROR: (' + repr(e) + ')', common.logErorr)

    def get_xml(self, vxmldoc, vnode):
        try:
            common.dbg_log('channel_list::get_xml', 'enter_function')
            for chn in self.Data:
                chn.get_xml(vxmldoc, vnode)
            common.dbg_log('channel_list::get_xml', 'exit_function')
        except Exception, e:
            common.dbg_log('channel_list::get_xml', 'ERROR: (' + repr(e) + ')', common.logErorr)

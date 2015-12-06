# -*- coding: utf-8 -*-

import common
import channel
import settings
import parservsetv
from xml.dom import minidom
import xbmcgui
import xbmcaddon
import datetime

def refresh_channels():
    try:
        common.dbg_log('functions::refresh_channels', 'enter_function')
        common.set_busy(1)
        set = settings.settings()
        set.backup()
        xmldoc = set.parse()
        if xmldoc != None:
            set.remove_old_channels(xmldoc)
            chnlst = channel.channel_list()
            chnlst.load_channels_from_net()
            chnlst.save_channels_to_settings(xmldoc)
            set.save(xmldoc)
        common.set_busy(0)
        common.dbg_log('functions::refresh_channels', 'exit_function')
    except Exception, e:
        common.set_busy(0)
        common.dbg_log('functions::refresh_channels', 'ERROR: (' + repr(e) + ')', common.logErorr) 
        
def save_xmltv():
    try:
        common.dbg_log('functions::save_xmltv', 'enter_function')
        common.notify(common.__scriptname__, common.Lang(33001), 'IconInfo')
        pDialog = xbmcgui.DialogProgressBG()
        pDialog.create(common.Lang(33004), '')
        prs = parservsetv.parser(pDialog)
        prs.get_content()
        prs.save_xml()
        pDialog.close()
        common.notify(common.__scriptname__, common.Lang(33002), 'IconInfo')
        xbmcaddon.Addon(common.__scriptid__).setSetting("last_update",datetime.datetime.now().strftime('%Y%m%d'))
        if common.execute_script == 'true':
    	    common.dbg_log('functions::save_xmltv', 'execute script - ' + common.script_patch)
    	    common.execute(common.script_patch)
        common.dbg_log('functions::save_xmltv', 'exit_function')
    except Exception, e:
        common.notify(common.__scriptname__, common.Lang(33003), 'IconError')
        common.dbg_log('functions::save_xmltv', 'ERROR: (' + repr(e) + ')', common.logErorr)
        
def service_update_epg():
    try:
        common.dbg_log('functions::service_update_epg', 'enter_function') 
        if common.enable_service == 'true':
            week_day = datetime.date.today().isoweekday()
            cur_time = datetime.datetime.now().strftime('%H:%M')
            cur_date = datetime.datetime.now().strftime('%Y%m%d')
            if week_day == 1:
                enable_upd_week = common.enable_monday == 'true'
            elif week_day == 2:
                enable_upd_week = common.enable_tuesday == 'true'
            elif week_day == 3:
                enable_upd_week = common.enable_wednesday == 'true'
            elif week_day == 4:
                enable_upd_week = common.enable_thursday == 'true'
            elif week_day == 5:
                enable_upd_week = common.enable_friday == 'true'
            elif week_day == 6:
                enable_upd_week = common.enable_saturday == 'true'
            elif week_day == 7:
                enable_upd_week = common.enable_sunday == 'true'
            else:
                enable_upd_week = False
            enable_upd_time = common.run_time <= cur_time
            enable_upd_day = common.last_update != cur_date
            if enable_upd_time and enable_upd_week and enable_upd_day:
                save_xmltv()
        common.dbg_log('functions::service_update_epg', 'exit_function')
    except Exception, e:
        common.dbg_log('functions::service_update_epg', 'ERROR: (' + repr(e) + ')', common.logErorr)
        
def run_update_epg():
    try:
        common.dbg_log('functions::run_update_epg', 'enter_function')
        dialog = xbmcgui.Dialog()
        if dialog.yesno(common.__scriptname__, common.Lang(33000)):
            save_xmltv()
        common.dbg_log('functions::run_update_epg', 'exit_function')
    except Exception, e:
        common.dbg_log('functions::run_update_epg', 'ERROR: (' + repr(e) + ')', common.logErorr)


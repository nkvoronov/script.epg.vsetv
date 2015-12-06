# -*- coding: utf-8 -*-

import os
import sys
import locale
import urllib2
import traceback
import subprocess
import xbmc
import xbmcaddon
import xbmcgui

__author__ = 'YLLOW_DRAGON'
__scriptname__ = 'Vse TV'
__scriptid__ = 'script.epg.vsetv'
__addon__ = xbmcaddon.Addon(__scriptid__)
__cwd__ = __addon__.getAddonInfo('path')
__common__ = sys.modules[globals()['__name__']]
__resources__ = xbmc.translatePath(os.path.join(__cwd__, 'resources'))
__media__ = xbmc.translatePath(os.path.join(__resources__, 'media'))
__icons__ = xbmc.translatePath(os.path.join(__media__, 'icons'))
__resources_lib__ = xbmc.translatePath(os.path.join(__resources__, 'lib'))
__settings_xml__  = xbmc.translatePath(os.path.join(__resources__, 'settings.xml'))

is_service = False
__busy__ = 0
input_request = False
logErorr = xbmc.LOGERROR

host = 'http://www.vsetv.com/'
useragent = 'Mozilla/5.0 (Windows NT 6.1; rv:5.0) Gecko/20100101 Firefox/5.0'
contenttype = 'application/x-www-form-urlencoded'

debug = __addon__.getSetting("debug")
xmltv_patch = __addon__.getSetting("xmltv_patch")
count_day = int(__addon__.getSetting("count_day"))+1
full_desc = __addon__.getSetting("full_desc")
lang = __addon__.getSetting("lang")
correction = int(__addon__.getSetting("correct"))*60
repspecsym = __addon__.getSetting("replace_spec_sym")
sort_by_index = __addon__.getSetting("sort_by_index")

last_update = __addon__.getSetting("last_update")
enable_service = __addon__.getSetting("enable_service")
enable_monday = __addon__.getSetting("enable_monday")
enable_tuesday = __addon__.getSetting("enable_tuesday")
enable_wednesday = __addon__.getSetting("enable_wednesday")
enable_thursday = __addon__.getSetting("enable_thursday")
enable_friday = __addon__.getSetting("enable_friday")
enable_saturday = __addon__.getSetting("enable_saturday")
enable_sunday = __addon__.getSetting("enable_sunday")
run_time = __addon__.getSetting("run_time")

execute_script = __addon__.getSetting("execute_script")
script_patch = __addon__.getSetting("script_patch")

sys.path.append(__resources_lib__)

encoding = locale.getpreferredencoding(do_setlocale=True)
reload(sys)
sys.setdefaultencoding(encoding)

def Lang(vcode):
    return __addon__.getLocalizedString(vcode)
    
def dbg_log(vsource, vtext, vlevel=xbmc.LOGNOTICE):
    if debug == 'false':
        return
    xbmc.log('## Vse TV ## ' + vsource + ' ## ' + vtext, vlevel)
    xbmc.log(traceback.format_exc())


def notify(vtitle, vmessage, vicon='icon', vtime=5000):
    try:
        dbg_log('common::notify', 'enter_function')
        picon = xbmc.translatePath(os.path.join(__icons__, vicon + '.png'))
        xbmcgui.Dialog().notification(vtitle, vmessage, picon, vtime)
        dbg_log('common::notify', 'exit_function')
    except Exception, e:
        dbg_log('common::notify', 'ERROR: (' + repr(e) + ')', logErorr)
        
def execute(vcommand_line, vget_result=0):
    try:
        dbg_log('common::execute', 'enter_function')
        dbg_log('common::execute::command', vcommand_line)
        if vget_result == 0:
            process = subprocess.Popen(vcommand_line, shell=True, close_fds=True)
            process.wait()
        else:
            result = ''
            process = subprocess.Popen(vcommand_line, shell=True, close_fds=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            process.wait()
            for line in process.stdout.readlines():
                result = result + line
            return result
        dbg_log('common::execute', 'exit_function')
    except Exception, e:
        dbg_log('common::execute', 'ERROR: (' + repr(e) + ')', logErorr)
        
def load_file(vfilename):
    try:
        if os.path.isfile(vfilename):
            objFile = open(vfilename, 'r')
            content = objFile.read()
            objFile.close()
        else:
            content = ''
        return content.strip()
    except Exception, e:
        dbg_log('common::load_file(' + vfilename + ')', 'ERROR: (' + repr(e) + ')', logErorr)
        
def load_url(vurl):
    try:
        request = urllib2.Request(vurl)
        request.add_header('User-Agent', useragent)
        request.add_header('Content-Type', contenttype)
        response = urllib2.urlopen(request)
        content = response.read()
        return content.strip()
    except Exception, e:
        dbg_log('common::load_url(' + vurl + ')', 'ERROR: (' + repr(e) + ')', logErorr)
               
def set_busy(vstate):
    global __busy__, __common__, input_request, is_service
    try:
        if not is_service:
            if vstate == 1:
                __busy__ = __busy__ + 1
            else:
                __busy__ = __busy__ - 1
            dbg_log('common::set_busy', '__busy__ = ' + unicode(__busy__))
            if __busy__ > 0:
                if not input_request:
                    xbmc.executebuiltin('ActivateWindow(busydialog)')
            else:
                xbmc.executebuiltin('Dialog.Close(busydialog)')
    except Exception, e:
        dbg_log('common::set_busy', 'ERROR: (' + repr(e) + ')', logErorr)
        
def remove_specsym(vstr):
    try: 
        dbg_log('common::remove_specsym', 'enter_function')
        rstr = vstr.strip('&nbsp;')
        rstr = rstr.replace('&amp;', '&')
        rstr = rstr.replace('&quot;','"')
        rstr = rstr.replace('&lt;', '<')
        rstr = rstr.replace('&gt;', '>')
        dbg_log('common::remove_specsym', 'exit_function')
        return rstr        
    except Exception, e:
        dbg_log('common::remove_specsym', 'ERROR: (' + repr(e) + ')', logErorr)
        return vstr

def save_xmlfile(vfilename, vxmldoc):
    try:
        dbg_log('common::save_xmlfile', 'enter_function')
        outputfile = open(vfilename, 'w')
        data = vxmldoc.toprettyxml(encoding='utf-8')
        if repspecsym == 'true':
            outputfile.write(remove_specsym(data))
        else:
            outputfile.write(data)
        outputfile.close() 
        dbg_log('common::save_xmlfile', 'exit_function')
    except Exception, e:
        dbg_log('common::save_xmlfile', 'ERROR: (' + repr(e) + ')', logErorr)
# -*- coding: utf-8 -*-

import common

class programme:
    __slots__ = ('ChannelIdx', 'Start', 'Stop', 'Title', 'Desc', 'UrlDesc', 'FullDesc', 'CategoryLang1', 'CategoryLang2', 'Directors', 'Actors', 'Date', 'Starrating')

    def __init__(self, vChannelIdx, vStart, vTitle, vStop='', vDesc='', vFullDesc='', vCategoryLang1='', vCategoryLang2='', vDirectors='', vActors='', vDate='', vStarrating=''):
        try:
            self.ChannelIdx = vChannelIdx
            self.Start = vStart
            self.Stop = vStop
            self.Title = vTitle
            self.Desc = vDesc
            self.UrlDesc = ''
            self.FullDesc = vFullDesc
            self.CategoryLang1 = vCategoryLang1
            self.CategoryLang2 = vCategoryLang2
            self.Directors = vDirectors
            self.Actors = vActors
            self.Date = vDate
            self.Starrating = vStarrating
        except Exception, e:
            common.dbg_log('programme::__init__', 'ERROR: (' + repr(e) + ')', common.logErorr)
            
    def copy_fulldesc(self, vprg):
        try:
            common.dbg_log('programme_list::copy_fulldesc', 'enter_function')
            self.UrlDesc = vprg.UrlDesc
            self.FullDesc = vprg.FullDesc
            self.CategoryLang1 = vprg.CategoryLang1
            self.CategoryLang2 = vprg.CategoryLang2
            self.Directors = vprg.Directors
            self.Actors = vprg.Actors
            self.Date = vprg.Date
            self.Starrating = vprg.Starrating
            common.dbg_log('programme_list::copy_fulldesc', 'exit_function')
        except Exception, e:
            common.dbg_log('programme_list::copy_fulldesc', 'ERROR: (' + repr(e) + ')', common.logErorr)
            
    def get_xml(self, vxmldoc, vnode):
        try:
            common.dbg_log('programme::get_xml', 'enter_function')            
            astr = ''        
            eprogramme = vxmldoc.createElement("programme")
            eprogramme.setAttribute("start", self.Start)
            eprogramme.setAttribute("stop", self.Stop)
            eprogramme.setAttribute("channel", self.ChannelIdx)        
            etittle = vxmldoc.createElement("title")
            etittle.setAttribute("lang", 'ru')        
            etittle_text = vxmldoc.createTextNode(self.Title)
            etittle.appendChild(etittle_text)
            eprogramme.appendChild(etittle) 
            if self.Desc != '':
                edesc = vxmldoc.createElement("desc")
                edesc.setAttribute("lang", 'ru')
                edesc_text = vxmldoc.createTextNode(self.Desc)
                edesc.appendChild(edesc_text)
                eprogramme.appendChild(edesc)           
            if self.FullDesc != '':
                edesc = vxmldoc.createElement("desc")
                edesc.setAttribute("lang", 'ru')
                edesc_text = vxmldoc.createTextNode(self.FullDesc)
                edesc.appendChild(edesc_text)
                eprogramme.appendChild(edesc)                              
            if (self.Directors != '') or (self.Actors != ''):
                ecredits = vxmldoc.createElement("credits")            
                if self.Directors != '':
                    strlist = self.Directors.split(',')                
                    for astr in strlist:
                        edirector = vxmldoc.createElement("director")
                        edirector_text = vxmldoc.createTextNode(astr.strip())
                        edirector.appendChild(edirector_text)
                        ecredits.appendChild(edirector)
                if self.Actors != '':
                    strlist = self.Actors.split(',')                
                    for astr in strlist:
                        eactor = vxmldoc.createElement("actor")
                        eactor_text = vxmldoc.createTextNode(astr.strip())
                        eactor.appendChild(eactor_text)
                        ecredits.appendChild(eactor)
                eprogramme.appendChild(ecredits)
            if self.Date != '':
                edate = vxmldoc.createElement("date")
                edate_text = vxmldoc.createTextNode(self.Date)
                edate.appendChild(edate_text)
                eprogramme.appendChild(edate)
            if self.CategoryLang2 != '':
                ecategory2 = vxmldoc.createElement("category")
                ecategory2.setAttribute("lang", 'en')
                ecategory2_text = vxmldoc.createTextNode(self.CategoryLang2)
                ecategory2.appendChild(ecategory2_text)
                eprogramme.appendChild(ecategory2)
            if self.CategoryLang1 != '':
                strlist = self.CategoryLang1.split(',')
                for astr in strlist:
                    ecategory1 = vxmldoc.createElement("category")
                    ecategory1.setAttribute("lang", 'ru')
                    ecategory1_text = vxmldoc.createTextNode(astr.strip().capitalize())
                    ecategory1.appendChild(ecategory1_text)
                    eprogramme.appendChild(ecategory1)
            if self.Starrating != '':
                erating = vxmldoc.createElement("star-rating")
                evalue = vxmldoc.createElement("value")
                evalue_text = vxmldoc.createTextNode(self.Starrating)
                evalue.appendChild(evalue_text)
                erating.appendChild(evalue)
                eprogramme.appendChild(erating)            
            vnode.appendChild(eprogramme) 
            common.dbg_log('programme::get_xml', 'exit_function')            
        except Exception, e:
            common.dbg_log('programme::get_xml', 'ERROR: (' + repr(e) + ')', common.logErorr)
            
class programme_list:
    __slots__ = ('Data')

    def __init__(self):
        try:
            self.Data = []
        except Exception, e:
            common.dbg_log('programme_list::__init__', 'ERROR: (' + repr(e) + ')', common.logErorr) 
            
    def set_programme_stop(self):
        try:
            common.dbg_log('programme_list::set_programme_stop', 'enter_function')
            i = 0        
            while i != len(self.Data):            
                dp1 = self.Data[i]            
                if i + 1 != len(self.Data):
                    dp2 = self.Data[i + 1]                
                    if dp1.ChannelIdx == dp2.ChannelIdx:
                        dp1.Stop = dp2.Start                   
                i += 1
            common.dbg_log('programme_list::set_programme_stop', 'exit_function')
        except:
            common.dbg_log('programme_list::set_programme_stop', 'ERROR: (' + repr(e) + ')', common.logErorr)       

    def get_xml(self, vxmldoc, vnode):
        try:
            common.dbg_log('programme_list::get_xml', 'enter_function')
            for prg in self.Data:
                prg.get_xml(vxmldoc, vnode)
            common.dbg_log('programme_list::get_xml', 'exit_function')
        except Exception, e:
            common.dbg_log('programme_list::get_xml', 'ERROR: (' + repr(e) + ')', common.logErorr)
            
    def get_programme_for_url(self, vurl):
        try:
            common.dbg_log('programme_list::get_programme_for_url', 'enter_function')
            for prg in self.Data:
                if prg.UrlDesc == vurl:
                    common.dbg_log('programme_list::get_programme_for_url', '*FOUND* exit_function')
                    return prg
            common.dbg_log('programme_list::get_programme_for_url', '*NO FOUND* exit_function')
            return None
        except Exception, e:
            common.dbg_log('programme_list::get_programme_for_url', 'ERROR: (' + repr(e) + ')', common.logErorr)
            return None
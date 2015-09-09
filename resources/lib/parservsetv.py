# -*- coding: utf-8 -*-

import re
import datetime
import common
import channel
import programme
from xml.dom import minidom
import xbmcgui

class parser:
    __slots__ = ('Progress', 'Channels', 'Programmes', 'CountDay', 'FullDesc', 'XMLOut')

    def __init__(self, vProgress):
        try:
            self.Progress = vProgress
            self.Channels = channel.channel_list()            
            self.Programmes = programme.programme_list()
            self.CountDay = common.count_day
            self.FullDesc = common.full_desc
            self.XMLOut = common.xmltv_patch
            self.Channels.load_channels_from_settings()
        except Exception, e:
            common.dbg_log('parser::__init__', 'ERROR: (' + repr(e) + ')', common.logErorr)
            
    def remove_tags(self, vstr):
        try: 
            common.dbg_log('parser::remove_tags', 'enter_function')
            rstr = re.sub('<([^!>]([^>]|\n)*)>', '', vstr)
            common.dbg_log('parser::remove_tags', 'exit_function')
            return rstr            
        except Exception, e:
            common.dbg_log('parser::remove_tags', 'ERROR: (' + repr(e) + ')', common.logErorr)
            return vstr
            
    def parse_strings(self, vstr, vbegin, vend, vrtags=0): 
        try:
            common.dbg_log('parser::parse_strings', 'enter_function')
            idx_beg = vstr.find(vbegin)
            idx_end = vstr.find(vend)
            rstr = vstr[idx_beg:idx_end]
            if vrtags == 1:
                rstr = self.remove_tags(rstr)
            common.dbg_log('parser::parse_strings', 'exit_function')
            return rstr.strip(' \t\n\r')
        except Exception, e:
            common.dbg_log('parser::parse_strings', 'ERROR: (' + repr(e) + ')', common.logErorr)
            return vstr        
                        
    def addzero(self, vstr):
        try:
            common.dbg_log('parser::addzero', 'enter_function')
            if vstr < 10:
                rstr = '0' + str(vstr)            
            else:
                rstr = str(vstr) 
            common.dbg_log('parser::addzero', 'exit_function')
            return rstr            
        except Exception, e:
            common.dbg_log('parser::addzero', 'ERROR: (' + repr(e) + ')', common.logErorr)
            return '00'

    # Даты начала передачи (start) и окончания передачи (stop) описываются в формате "YmdHis P",
    # где Y — год (4-значный), m — месяц (от 01 до 12), d — день (от 01 до 31), H — час (от 00 до 23), i — минута (от 00 до 59), s — секунда (от 00 до 59),
    # P — смещение по часовому поясу (+0400 — соответствует Московскому времени).
    # 20131125144000 +0200 
    
    def get_datetime_fmt(self, vdate, vtimestr, vcorrection):
        try:
            common.dbg_log('parser::get_datetime_fmt', 'enter_function')
            vdatestr = vdate.strftime('%Y%m%d') + vtimestr.replace(':','')
            crh = vcorrection // 60
            crm = vcorrection - crh * 60        
            if crh >= 0:
                dstr = '+' + self.addzero(crh) + self.addzero(crm)            
            else:
                dstr = '-' + self.addzero(crh) + self.addzero(crm)            
            vdatestr = vdatestr + ' ' + dstr
            common.dbg_log('parser::get_datetime_fmt', 'exit_function')
            return vdatestr           
        except Exception, e:
            common.dbg_log('parser::get_datetime_fmt', 'ERROR: (' + repr(e) + ')', common.logErorr)
            return '00000000000000 +0000'

    def get_content(self):
        try:
            common.dbg_log('parser::get_content', 'enter_function')
            i = 0
            p = 0
            loops = self.CountDay*len(self.Channels.Data)
            for dc in self.Channels.Data:
                nowdt = datetime.datetime.now()
                curdt = nowdt           
                while curdt != nowdt + datetime.timedelta(days=self.CountDay):
                    p = int(100 * float(i)/float(loops-1))
                    self.Progress.update(p, common.Lang(33004), dc.OName + ' - ' + curdt.strftime('%d.%m.%Y'))
                    self.get_content_day(dc, curdt)
                    curdt = curdt + datetime.timedelta(days=1)
                    i += 1
            self.Programmes.set_programme_stop()        
            common.dbg_log('parser::get_content', 'exit_function') 
        except Exception, e:
            common.dbg_log('parser::get_content', 'ERROR: (' + repr(e) + ')', common.logErorr)
    
    def get_content_day(self,  vchanneldata, vdate):
        try:
            common.dbg_log('parser::get_content_day', 'enter_function')
            ltime = '00:00'
            ctimeb = '00:00'
            ctimee = '00:00'
            ctitle = ''
            vdirection = 'schedule_channel_%s_day_%s.html' % (vchanneldata.Index, vdate.strftime('%Y-%m-%d'))
            common.dbg_log('parser::get_content_day', common.host+vdirection)
            html = common.load_url(common.host+vdirection)
            html = html.decode('windows-1251').encode('utf-8')
            if self.FullDesc == 'true':            
                prdata = re.compile('<div class="(?:pasttime|onair|time)">(.+?)</div><div class="(?:pastprname2|prname2)">(.+?)</div>').findall(html)
                for ctimeb, prtitle in prdata:
                    if ctimeb < ltime:
                        vdate = vdate + datetime.timedelta(days=1)                    
                    ltime = ctimeb
                    oprtitle = prtitle
                    ctimeb = self.get_datetime_fmt(vdate, ctimeb + ':00', common.correction)
                    ctimee = self.get_datetime_fmt(vdate, '23:59:59', common.correction)           
                    ctitle = common.remove_specsym(self.remove_tags(prtitle))
                    prog = programme.programme(vchanneldata.Index, ctimeb, ctitle.decode('utf-8'), ctimee)
                    self.get_category_from_title(prog)
                    self.get_fulldesc(prog, oprtitle)                   
                    self.Programmes.Data.append(prog) 
            else:
                prdata = re.compile('<div class="(?:pasttime|onair|time)">(.+?)</div><div class="(?:pastprname2|prname2)">(.+?)(?:</div><div id=desc\d{16} class="(?:pastdesc|prdesc)"><div class="desc"><b>(.+?)</div></div>|</div>)').findall(html)
                for ctimeb, prtitle, prdesc in prdata:                
                    if ctimeb < ltime:
                        vdate = vdate + datetime.timedelta(days=1)                    
                    ltime = ctimeb
                    oprtitle = prtitle
                    ctimeb = self.get_datetime_fmt(vdate, ctimeb + ':00', common.correction)
                    ctimee = self.get_datetime_fmt(vdate, '23:59:59', common.correction)           
                    ctitle = common.remove_specsym(self.remove_tags(prtitle))
                    prog = programme.programme(vchanneldata.Index, ctimeb, ctitle.decode('utf-8'), ctimee)                                                        
                    self.get_category_from_title(prog)
                    self.get_desc(prog, prdesc.decode('utf-8'))
                    self.Programmes.Data.append(prog)            
            common.dbg_log('parser::get_content_day', 'exit_function') 
        except Exception, e:
            common.dbg_log('parser::get_content_day', 'ERROR: (' + repr(e) + ')', common.logErorr)
            
    def get_desc(self, vprogrammedata, vcontent):
        try:
            common.dbg_log('parser::get_desc', 'enter_function')
            if vcontent != '':
                vdesc = vcontent.replace('<br>', ' ')
                vdesc = common.remove_specsym(self.remove_tags(vdesc))
                vprogrammedata.Desc = vdesc
            common.dbg_log('parser::get_desc', 'exit_function')
        except Exception, e:
            common.dbg_log('parser::get_desc', 'ERROR: (' + repr(e) + ')', common.logErorr)        
    
    def get_fulldesc(self, vprogrammedata, vcontent):
        try:
            common.dbg_log('parser::get_fulldesc', 'enter_function')
            idx_beg = vcontent.find('<a href=')
            if idx_beg != -1:
                idx_end = vcontent.find('.html')
                url = vcontent[idx_beg+8:idx_end]+'.html'
                sprg = self.Programmes.get_programme_for_url(url)
                if sprg != None:
                    vprogrammedata.copy_fulldesc(sprg)
                else:
                    html = common.load_url(common.host+url)
                    html = html.decode('windows-1251').encode('utf-8')
                    vprogrammedata.UrlDesc = url
                    showname = '<td colspan="2" valign="top" class="showname">'
                    showmain = '<td width="700" valign="top" class="showmain">'
                    showname1 = self.parse_strings(html,showname,showmain)
                    ctmp = ''
                    ccountry = ''
                    cdate = ''
                    if showname1.find('<strong>') != -1:
                        ctmp = self.parse_strings(showname1,'<br>','<strong>',1).strip(',')
                    else:
                        ctmp = self.parse_strings(showname1,'<br>','<!--',1).strip(',').replace('&nbsp;','')
                    if len(ctmp.split(','))==2:                     
                        ccountry = ctmp.split(',')[0].strip()
                        cdate = ctmp.split(',')[1].strip()
                        if cdate[-1] == '-':
                            cdate = cdate[:-1]           
                        if cdate != '':
                            ctmp = ccountry + ', ' + cdate
                            vprogrammedata.Date = cdate
                    ctmp = ctmp.decode('utf-8').strip(' \t\n\r')
                    cgenre = ''
                    cgenre = self.parse_strings(showname1,'<strong>','</strong>',1).replace(' / ', ',')
                    if cgenre != '':
                        cgenre = cgenre.decode('utf-8').strip(' \t\n\r')
                        if vprogrammedata.CategoryLang1 != '':
                            vprogrammedata.CategoryLang1 = vprogrammedata.CategoryLang1 + ',' + cgenre
                        else:
                            vprogrammedata.CategoryLang1 = cgenre
                    cdirectors = ''
                    cactors = ''
                    cdesc = ''
                    crat = ''
                    showmain1 = self.parse_strings(html,showmain,'<td valign="top">')
                    cdirectors = self.parse_strings(showmain1,'Режиссер(ы):','<br>',1)
                    if cdirectors != '':
                        vprogrammedata.Directors = cdirectors.decode('utf-8')[12:].strip().strip(' \t\n\r')                        
                    cactors = self.parse_strings(showmain1,'Актеры:','<div>',1)
                    if cactors != '':
                        vprogrammedata.Actors = cactors.decode('utf-8')[7:].strip().strip(' \t\n\r') 
                    cactors1 = self.parse_strings(showmain1,'Ведущие:','<div>',1)
                    if cactors1 != '':
                        if vprogrammedata.Actors != '':
                            vprogrammedata.Actors = vprogrammedata.Actors + cactors1.decode('utf-8')[8:].strip().strip(' \t\n\r')
                        else:
                            vprogrammedata.Actors = cactors1.decode('utf-8')[8:].strip().strip(' \t\n\r')
                    cdesc = self.parse_strings(showmain1,'<span class="big">','<span class="name">',1)
                    if ctmp !='':
                        vprogrammedata.FullDesc = ctmp + '. ' + cdesc.decode('utf-8').strip().strip(' \t\n\r')
                    else:
                        vprogrammedata.FullDesc = cdesc.decode('utf-8').strip().strip(' \t\n\r')
                    crat = self.parse_strings(showmain1,'<span class="name">','Проголосовало',1)
                    if len(crat.decode('utf-8').split(':'))>1:
                        crat = crat.decode('utf-8').split(':')[1].strip().strip(' \t\n\r')
                    else:
                        crat = ''
                    if crat != '':
                        vprogrammedata.Starrating = crat
            common.dbg_log('parser::get_fulldesc', 'exit_function')
        except Exception, e:
            common.dbg_log('parser::get_fulldesc', 'ERROR: (' + repr(e) + ')', common.logErorr)
    
    def get_category_from_title(self, vprogrammedata):
        try:
            common.dbg_log('parser::get_category_from_title', 'enter_function')
            vtitle = vprogrammedata.Title.encode('utf-8').lower()
            if (vtitle.find('х/ф') != -1) or (vtitle.find('д/ф') != -1) or \
            (vtitle.find('Х/ф') != -1) or (vtitle.find('Д/ф') != -1):
                if vprogrammedata.CategoryLang1 != '':
                    vprogrammedata.CategoryLang1 = vprogrammedata.CategoryLang1 + ',фильм'.decode('utf-8')
                else:
                    vprogrammedata.CategoryLang1 = 'фильм'.decode('utf-8')
                vprogrammedata.CategoryLang2 = 'Movie / Drama'            
            elif (vtitle.find('т/с') != -1) or (vtitle.find('х/с') != -1) or (vtitle.find('д/с') != -1) or \
            (vtitle.find('Т/с') != -1) or (vtitle.find('Х/с') != -1) or (vtitle.find('Д/с') != -1):
                if vprogrammedata.CategoryLang1 != '':
                    vprogrammedata.CategoryLang1 = vprogrammedata.CategoryLang1 + ',сериал'.decode('utf-8')
                else:
                    vprogrammedata.CategoryLang1 = 'сериал'.decode('utf-8')
                vprogrammedata.CategoryLang2 = 'Movie / Drama'            
            elif (vtitle.find('м/ф') != -1) or (vtitle.find('м/с') != -1) or \
            (vtitle.find('М/ф') != -1) or (vtitle.find('М/с') != -1) or (vtitle.find('мульт') != -1):
                if vprogrammedata.CategoryLang1 != '':
                    vprogrammedata.CategoryLang1 = vprogrammedata.CategoryLang1 + ',мультфильм'.decode('utf-8')
                else:
                    vprogrammedata.CategoryLang1 = 'мультфильм'.decode('utf-8')
                vprogrammedata.CategoryLang2 = 'Cartoons / Puppets'            
            elif (vtitle.find('спорт') != -1) or (vtitle.find('футбол') != -1) or (vtitle.find('хоккей') != -1) or (vtitle.find('uefa') != -1) or \
            (vtitle.find('Спорт') != -1) or (vtitle.find('Футбол') != -1) or (vtitle.find('Хоккей') != -1):
                if vprogrammedata.CategoryLang1 != '':
                    vprogrammedata.CategoryLang1 = vprogrammedata.CategoryLang1 + ',спорт'.decode('utf-8')
                else:
                    vprogrammedata.CategoryLang1 = 'спорт'.decode('utf-8')
                vprogrammedata.CategoryLang2 = 'Sports'            
            elif (vtitle.find('новост') != -1) or (vtitle.find('факты') != -1) or (vtitle.find('тсн') != -1) or (vtitle.find('новини') != -1) or (vtitle.find('время') != -1) or (vtitle.find('известия') != -1) or \
            (vtitle.find('Новост') != -1) or (vtitle.find('Факты') != -1) or (vtitle.find('ТСН') != -1)  or (vtitle.find('Новини') != -1) or (vtitle.find('Время') != -1) or (vtitle.find('Известия') != -1):
                if vprogrammedata.CategoryLang1 != '':
                    vprogrammedata.CategoryLang1 = vprogrammedata.CategoryLang1 + ',новости'.decode('utf-8')
                else:
                    vprogrammedata.CategoryLang1 = 'новости'.decode('utf-8')
                vprogrammedata.CategoryLang2 = 'News / Current affairs'            
            elif (vtitle.find('истори') != -1) or (vtitle.find('планет') != -1) or (vtitle.find('разрушители') != -1) or (vtitle.find('знаки') != -1) or (vtitle.find('катастроф') != -1):
                if vprogrammedata.CategoryLang1 != '':
                    vprogrammedata.CategoryLang1 = vprogrammedata.CategoryLang1 + ',досуг'.decode('utf-8')
                else:
                    vprogrammedata.CategoryLang1 = 'досуг'.decode('utf-8')
                vprogrammedata.CategoryLang2 = 'Leisure hobbies'            
            else:
                vprogrammedata.CategoryLang2 = ''
            common.dbg_log('parser::get_category_from_title', 'exit_function')
        except Exception, e:
            common.dbg_log('parser::get_category_from_title', 'ERROR: (' + repr(e) + ')', common.logErorr)
    
    def save_xml(self):
        try:
            common.dbg_log('parser::save_xml', 'enter_function')
            xmldoc = minidom.parseString('<tv generator-info-name="vsetv"></tv>')
            self.Channels.get_xml(xmldoc, xmldoc.documentElement)
            self.Programmes.get_xml(xmldoc, xmldoc.documentElement)
            common.save_xmlfile(self.XMLOut, xmldoc)           
            common.dbg_log('parser::save_xml', 'enter_function')
        except Exception, e:
            common.dbg_log('parser::save_xml', 'ERROR: (' + repr(e) + ')', common.logErorr)
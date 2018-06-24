# -*- coding: utf-8 -*-

import os
import re
import datetime
import xbmc
from common import Base, logErorr, host
from channels import Channel, ChannelList
from programmes import ProgrammeList, Programme
from xml.dom import minidom

class Parser(Base):

    def __init__(self, progress):
        try:
            Base.__init__(self)
            self._progress = progress
            self._channels = ChannelList()
            self._programmes = ProgrammeList()
            self._countDay = int(self._addon.getSetting('count_day')) + 1
            self._fullDesc = self._addon.getSetting('full_desc')
            self._pathXml = xbmc.translatePath(os.path.join(self._addon.getSetting('xmltv_path'), 'xmltv.xml'))
            self._channels.loadChannelsFromFile(0)
        except Exception, e:
            self.addLog('Parser::__init__', 'ERROR: (' + repr(e) + ')', logErorr)

    def removeTags(self, mstr):
        try:
            self.addLog('Parser::removeTags', 'enter_function')
            rstr = re.sub('<([^!>]([^>]|\n)*)>', '', mstr)
            self.addLog('Parser::removeTags', 'exit_function')
            return rstr
        except Exception, e:
            self.addLog('Parser::removeTags', 'ERROR: (' + repr(e) + ')', logErorr)
            return vstr

    def parseStrings(self, mstr, begin, end, rtags=0):
        try:
            self.addLog('Parser::parseStrings', 'enter_function')
            idx_beg = mstr.find(begin)
            idx_end = mstr.find(end)
            rstr = mstr[idx_beg:idx_end]
            if rtags == 1:
                rstr = self.removeTags(rstr)
            self.addLog('Parser::parseStrings', 'exit_function')
            return rstr.strip(' \t\n\r')
        except Exception, e:
            self.addLog('Parser::parseStrings', 'ERROR: (' + repr(e) + ')', logErorr)
            return vstr

    def addZero(self, mstr):
        try:
            self.addLog('Parser::addZero', 'enter_function')
            if mstr < 10:
                rstr = '0' + str(mstr)
            else:
                rstr = str(mstr)
            self.addLog('Parser::addZero', 'exit_function')
            return rstr
        except Exception, e:
            self.addLog('Parser::addZero', 'ERROR: (' + repr(e) + ')', logErorr)
            return '00'

    # Даты начала передачи (start) и окончания передачи (stop) описываются в формате "YmdHis P",
    # где Y — год (4-значный), m — месяц (от 01 до 12), d — день (от 01 до 31), H — час (от 00 до 23), i — минута (от 00 до 59), s — секунда (от 00 до 59),
    # P — смещение по часовому поясу (+0400 — соответствует Московскому времени).
    # 20131125144000 +0200

    def getDateTimeFmt(self, date, timestr, correction):
        try:
            self.addLog('Parser::getDateTimeFmt', 'enter_function')
            datestr = date.strftime('%Y%m%d') + timestr.replace(':','')
            crh = correction // 60
            crm = correction - crh * 60
            if crh >= 0:
                dstr = '+' + self.addZero(crh) + self.addZero(crm)
            else:
                dstr = '-' + self.addZero(crh) + self.addZero(crm)
            datestr = datestr + ' ' + dstr
            self.addLog('Parser::getDateTimeFmt', 'exit_function')
            return datestr
        except Exception, e:
            self.addLog('Parser::getDateTimeFmt', 'ERROR: (' + repr(e) + ')', logErorr)
            return '00000000000000 +0000'

    def getContent(self):
        try:
            self.addLog('Parser::getContent', 'enter_function')
            i = 0
            p = 0
            loops = self._countDay * len(self._channels._data)
            for dc in self._channels._data:
                nowdt = datetime.datetime.now()
                curdt = nowdt
                while curdt != nowdt + datetime.timedelta(days=self._countDay):
                    p = int(100 * float(i)/float(loops - 1))
                    self._progress.update(p, self.getLang(33004), dc._orgName + ' - ' + curdt.strftime('%d.%m.%Y'))
                    self.getContentDay(dc, curdt)
                    curdt = curdt + datetime.timedelta(days=1)
                    i += 1
            self._programmes.setProgrammeStop()
            self.addLog('Parser::getContent', 'exit_function')
        except Exception, e:
            self.addLog('Parser::getContent', 'ERROR: (' + repr(e) + ')', logErorr)

    def getContentDay(self, channeldata, date):
        try:
            self.addLog('Parser::getContentDay', 'enter_function')
            ltime = '00:00'
            ctimeb = '00:00'
            ctimee = '00:00'
            ctitle = ''
            direction = 'schedule_channel_%s_day_%s.html' % (channeldata._index, date.strftime('%Y-%m-%d'))
            self.addLog('Parser::getContentDay', host + direction)
            html = self.loadUrl(host + direction)
            html = html.decode('windows-1251').encode('utf-8')
            if self._fullDesc == 'true':
                prdata = re.compile('<div class="(?:pasttime|onair|time)">(.+?)</div><div class="(?:pastprname2|prname2)">(.+?)</div>').findall(html)
                for ctimeb, prtitle in prdata:
                    if ctimeb < ltime:
                        date = date + datetime.timedelta(days=1)
                    ltime = ctimeb
                    oprtitle = prtitle
                    ctimeb = self.getDateTimeFmt(date, ctimeb + ':00', int(channeldata._correction))
                    ctimee = self.getDateTimeFmt(date, '23:59:59', int(channeldata._correction))
                    ctitle = self.removeSpecSym(self.removeTags(prtitle))
                    prog = Programme(channeldata._index, ctimeb, ctitle.decode('utf-8'), ctimee)
                    self.getCategoryFromTitle(prog)
                    self.getFullDesc(prog, oprtitle)
                    self._programmes._data.append(prog)
            else:
                prdata = re.compile('<div class="(?:pasttime|onair|time)">(.+?)</div><div class="(?:pastprname2|prname2)">(.+?)(?:</div><div id=desc\d{16} class="(?:pastdesc|prdesc)"><div class="desc"><b>(.+?)</div></div>|</div>)').findall(html)
                for ctimeb, prtitle, prdesc in prdata:
                    if ctimeb < ltime:
                        date = date + datetime.timedelta(days=1)
                    ltime = ctimeb
                    oprtitle = prtitle
                    ctimeb = self.getDateTimeFmt(date, ctimeb + ':00', int(channeldata._correction))
                    ctimee = self.getDateTimeFmt(date, '23:59:59', int(channeldata._correction))
                    ctitle = self.removeSpecSym(self.removeTags(prtitle))
                    prog = Programme(channeldata._index, ctimeb, ctitle.decode('utf-8'), ctimee)
                    self.getCategoryFromTitle(prog)
                    self.getDesc(prog, prdesc.decode('utf-8'))
                    self._programmes._data.append(prog)
            self.addLog('Parser::getContentDay', 'exit_function')
        except Exception, e:
            self.addLog('Parser::getContentDay', 'ERROR: (' + repr(e) + ')', logErorr)

    def getDesc(self, programmedata, content):
        try:
            self.addLog('Parser::getDesc', 'enter_function')
            if content != '':
                desc = content.replace('<br>', ' ')
                desc = self.removeSpecSym(self.removeTags(vdesc))
                programmedata._desc = desc
            self.addLog('Parser::getDesc', 'exit_function')
        except Exception, e:
            self.addLog('Parser::getDesc', 'ERROR: (' + repr(e) + ')', logErorr)

    def getFullDesc(self, programmedata, content):
        try:
            self.addLog('Parser::getFullDesc', 'enter_function')
            idx_beg = content.find('<a href=')
            if idx_beg != -1:
                idx_end = content.find('.html')
                url = content[idx_beg+8:idx_end] + '.html'
                sprg = self._programmes.getProgrammeForUrl(url)
                if sprg != None:
                    programmedata.copyFullDesc(sprg)
                else:
                    html = self.loadUrl(host + url)
                    html = html.decode('windows-1251').encode('utf-8')
                    programmedata._urlDesc = url
                    showname = '<td colspan="2" valign="top" class="showname">'
                    showmain = '<td width="700" valign="top" class="showmain">'
                    showname1 = self.parseStrings(html,showname,showmain)
                    ctmp = ''
                    ccountry = ''
                    cdate = ''
                    if showname1.find('<strong>') != -1:
                        ctmp = self.parseStrings(showname1,'<br>','<strong>',1).strip(',')
                    else:
                        ctmp = self.parseStrings(showname1,'<br>','<!--',1).strip(',').replace('&nbsp;','')
                    if len(ctmp.split(',')) == 2:
                        ccountry = ctmp.split(',')[0].strip()
                        cdate = ctmp.split(',')[1].strip()
                        if cdate[-1] == '-':
                            cdate = cdate[:-1]
                        if cdate != '':
                            ctmp = ccountry + ', ' + cdate
                            programmedata._date = cdate
                    ctmp = ctmp.decode('utf-8').strip(' \t\n\r')
                    cgenre = ''
                    cgenre = self.parseStrings(showname1,'<strong>','</strong>',1).replace(' / ', ',')
                    if cgenre != '':
                        cgenre = cgenre.decode('utf-8').strip(' \t\n\r')
                        if programmedata._categoryLang1 != '':
                            programmedata._categoryLang1 = programmedata._categoryLang1 + ',' + cgenre
                        else:
                            programmedata._categoryLang1 = cgenre
                    cdirectors = ''
                    cactors = ''
                    cdesc = ''
                    crat = ''
                    showmain1 = self.parseStrings(html, showmain, '<td valign="top">')
                    cdirectors = self.parseStrings(showmain1, 'Режиссер(ы):', '<br>',1)
                    if cdirectors != '':
                        programmedata._directors = cdirectors.decode('utf-8')[12:].strip().strip(' \t\n\r')
                    cactors = self.parseStrings(showmain1, 'Актеры:', '<div>',1)
                    if cactors != '':
                        programmedata._actors = cactors.decode('utf-8')[7:].strip().strip(' \t\n\r')
                    cactors1 = self.parseStrings(showmain1,'Ведущие:','<div>',1)
                    if cactors1 != '':
                        if programmedata._actors != '':
                            programmedata._actors = programmedata.Actors + cactors1.decode('utf-8')[8:].strip().strip(' \t\n\r')
                        else:
                            programmedata._actors = cactors1.decode('utf-8')[8:].strip().strip(' \t\n\r')
                    cdesc = self.parseStrings(showmain1,'<span class="big">','<span class="name">',1)
                    if ctmp !='':
                        programmedata._fullDesc = ctmp + '. ' + cdesc.decode('utf-8').strip().strip(' \t\n\r')
                    else:
                        programmedata._fullDesc = cdesc.decode('utf-8').strip().strip(' \t\n\r')
                    crat = self.parseStrings(showmain1,'<span class="name">', 'Проголосовало',1)
                    if len(crat.decode('utf-8').split(':')) > 1:
                        crat = crat.decode('utf-8').split(':')[1].strip().strip(' \t\n\r')
                    else:
                        crat = ''
                    if crat != '':
                        programmedata._starrating = crat
            self.addLog('Parser::getFullDesc', 'exit_function')
        except Exception, e:
            self.addLog('Parser::getFullDesc', 'ERROR: (' + repr(e) + ')', logErorr)

    def getCategoryFromTitle(self, programmedata):
        try:
            self.addLog('Parser::getCategoryFromTitle', 'enter_function')
            title = programmedata._title.encode('utf-8').lower()
            if (title.find('х/ф') != -1) or (title.find('д/ф') != -1) or \
            (title.find('Х/ф') != -1) or (title.find('Д/ф') != -1):
                if programmedata._categoryLang1 != '':
                    programmedata._categoryLang1 = programmedata._categoryLang1 + ',фильм'.decode('utf-8')
                else:
                    programmedata._categoryLang1 = 'фильм'.decode('utf-8')
                programmedata._categoryLang2 = 'Movie / Drama'
            elif (title.find('т/с') != -1) or (title.find('х/с') != -1) or (title.find('д/с') != -1) or \
            (title.find('Т/с') != -1) or (title.find('Х/с') != -1) or (title.find('Д/с') != -1):
                if programmedata._categoryLang1 != '':
                    programmedata._categoryLang1 = programmedata._categoryLang1 + ',сериал'.decode('utf-8')
                else:
                    programmedata._categoryLang1 = 'сериал'.decode('utf-8')
                programmedata._categoryLang2 = 'Movie / Drama'
            elif (title.find('м/ф') != -1) or (title.find('м/с') != -1) or \
            (title.find('М/ф') != -1) or (title.find('М/с') != -1) or (title.find('мульт') != -1):
                if programmedata._categoryLang1 != '':
                    programmedata._categoryLang1 = programmedata._categoryLang1 + ',мультфильм'.decode('utf-8')
                else:
                    programmedata._categoryLang1 = 'мультфильм'.decode('utf-8')
                programmedata._categoryLang2 = 'Cartoons / Puppets'
            elif (title.find('спорт') != -1) or (title.find('футбол') != -1) or (title.find('хоккей') != -1) or (title.find('uefa') != -1) or \
            (title.find('Спорт') != -1) or (title.find('Футбол') != -1) or (title.find('Хоккей') != -1):
                if programmedata._categoryLang1 != '':
                    programmedata._categoryLang1 = programmedata._categoryLang1 + ',спорт'.decode('utf-8')
                else:
                    programmedata._categoryLang1 = 'спорт'.decode('utf-8')
                programmedata._categoryLang2 = 'Sports'
            elif (title.find('новост') != -1) or (title.find('факты') != -1) or (title.find('тсн') != -1) or (title.find('новини') != -1) or (title.find('время') != -1) or (title.find('известия') != -1) or \
            (title.find('Новост') != -1) or (title.find('Факты') != -1) or (title.find('ТСН') != -1) or (title.find('Т.С.Н.') != -1)  or (title.find('Новини') != -1) or (title.find('Время') != -1) or (title.find('Известия') != -1):
                if programmedata._categoryLang1 != '':
                    programmedata._categoryLang1 = programmedata._categoryLang1 + ',новости'.decode('utf-8')
                else:
                    programmedata._categoryLang1 = 'новости'.decode('utf-8')
                programmedata._categoryLang2 = 'News / Current affairs'
            elif (title.find('истори') != -1) or (title.find('планет') != -1) or (title.find('разрушители') != -1) or (title.find('знаки') != -1) or (title.find('катастроф') != -1):
                if programmedata._categoryLang1 != '':
                    programmedata._categoryLang1 = programmedata._categoryLang1 + ',досуг'.decode('utf-8')
                else:
                    programmedata._categoryLang1 = 'досуг'.decode('utf-8')
                programmedata._categoryLang2 = 'Leisure hobbies'
            else:
                programmedata._categoryLang2 = ''
            self.addLog('Parser::getCategoryFromTitle', 'exit_function')
        except Exception, e:
            self.addLog('Parser::getCategoryFromTitle', 'ERROR: (' + repr(e) + ')', logErorr)

    def saveXml(self):
        try:
            self.addLog('Parser::saveXml', 'enter_function')
            xmldoc = minidom.parseString('<tv generator-info-name="vsetv"></tv>')
            self._channels.getXml(xmldoc, xmldoc.documentElement)
            self._programmes.getXml(xmldoc, xmldoc.documentElement)
            self.saveXmlFile(self._pathXml, xmldoc)
            self.addLog('Parser::saveXml', 'enter_function')
        except Exception, e:
            self.addLog('Parser::saveXml', 'ERROR: (' + repr(e) + ')', logErorr)

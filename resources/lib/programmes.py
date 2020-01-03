# -*- coding: utf-8 -*-

from resources.lib.common import Base, logErorr
from xml.dom import minidom

class Programme(Base):

    def __init__(self, channelIdx, start, title, stop='', desc='', fullDesc='', categoryLang1='', categoryLang2='', directors='', actors='', date='', starrating=''):
        try:
            Base.__init__(self)
            self._channelIdx = channelIdx
            self._start = start
            self._stop = stop
            self._title = title
            self._desc = desc
            self._urlDesc = ''
            self._fullDesc = fullDesc
            self._categoryLang1 = categoryLang1
            self._categoryLang2 = categoryLang2
            self._directors = directors
            self._actors = actors
            self._date = date
            self._starrating = starrating
        except Exception as e:
            self.addLog('Programme::__init__', 'ERROR: (' + repr(e) + ')', logErorr)

    def copyFullDesc(self, prg):
        try:
            self.addLog('Programme::copyFullDesc', 'enter_function')
            self._urlDesc = prg._urlDesc
            self._fullDesc = prg._fullDesc
            self._categoryLang1 = prg._categoryLang1
            self._categoryLang2 = prg._categoryLang2
            self._directors = prg._directors
            self._actors = prg._actors
            self._date = prg._date
            self._starrating = prg._starrating
            self.addLog('Programme::copyFullDesc', 'exit_function')
        except Exception as e:
            self.addLog('Programme::copyFullDesc', 'ERROR: (' + repr(e) + ')', logErorr)

    def getXml(self, xmldoc, node):
        try:
            self.addLog('Programme::getXml', 'enter_function')
            astr = ''
            eprogramme = xmldoc.createElement('programme')
            eprogramme.setAttribute('start', self._start)
            eprogramme.setAttribute('stop', self._stop)
            eprogramme.setAttribute('channel', str(self._channelIdx))
            etittle = xmldoc.createElement('title')
            etittle.setAttribute('lang', 'ru')
            etittle_text = xmldoc.createTextNode(self._title)
            etittle.appendChild(etittle_text)
            eprogramme.appendChild(etittle)
            if self._desc != '':
                edesc = xmldoc.createElement('desc')
                edesc.setAttribute('lang', 'ru')
                edesc_text = xmldoc.createTextNode(self._desc)
                edesc.appendChild(edesc_text)
                eprogramme.appendChild(edesc)
            if self._fullDesc != '':
                edesc = xmldoc.createElement('desc')
                edesc.setAttribute('lang', 'ru')
                edesc_text = xmldoc.createTextNode(self._fullDesc)
                edesc.appendChild(edesc_text)
                eprogramme.appendChild(edesc)
            if (self._directors != '') or (self._actors != ''):
                ecredits = xmldoc.createElement('credits')
                if self._directors != '':
                    strlist = self._directors.split(',')
                    for astr in strlist:
                        edirector = xmldoc.createElement('director')
                        edirector_text = xmldoc.createTextNode(astr.strip())
                        edirector.appendChild(edirector_text)
                        ecredits.appendChild(edirector)
                if self._actors != '':
                    strlist = self._actors.split(',')
                    for astr in strlist:
                        eactor = xmldoc.createElement('actor')
                        eactor_text = xmldoc.createTextNode(astr.strip())
                        eactor.appendChild(eactor_text)
                        ecredits.appendChild(eactor)
                eprogramme.appendChild(ecredits)
            if self._date != '':
                edate = xmldoc.createElement('date')
                edate_text = xmldoc.createTextNode(self._date)
                edate.appendChild(edate_text)
                eprogramme.appendChild(edate)
            if self._categoryLang2 != '':
                ecategory2 = xmldoc.createElement('category')
                ecategory2.setAttribute('lang', 'en')
                ecategory2_text = xmldoc.createTextNode(self._categoryLang2)
                ecategory2.appendChild(ecategory2_text)
                eprogramme.appendChild(ecategory2)
            if self._categoryLang1 != '':
                strlist = self._categoryLang1.split(',')
                for astr in strlist:
                    ecategory1 = xmldoc.createElement('category')
                    ecategory1.setAttribute('lang', 'ru')
                    ecategory1_text = xmldoc.createTextNode(astr.strip().capitalize())
                    ecategory1.appendChild(ecategory1_text)
                    eprogramme.appendChild(ecategory1)
            if self._starrating != '':
                erating = xmldoc.createElement('star-rating')
                evalue = xmldoc.createElement('value')
                evalue_text = xmldoc.createTextNode(self._starrating)
                evalue.appendChild(evalue_text)
                erating.appendChild(evalue)
                eprogramme.appendChild(erating)
            node.appendChild(eprogramme)
            self.addLog('Programme::getXml', 'exit_function')
        except Exception as e:
            self.addLog('Programme::getXml', 'ERROR: (' + repr(e) + ')', logErorr)

class ProgrammeList(Base):

    def __init__(self):
        try:
            Base.__init__(self)
            self._data = []
        except Exception as e:
            self.addLog('ProgrammeList::__init__', 'ERROR: (' + repr(e) + ')', logErorr)

    def setProgrammeStop(self):
        try:
            self.addLog('ProgrammeList::setProgrammeStop', 'enter_function')
            i = 0
            while i != len(self._data):
                dp1 = self._data[i]
                if i + 1 != len(self._data):
                    dp2 = self._data[i + 1]
                    if dp1._channelIdx == dp2._channelIdx:
                        dp1._stop = dp2._start
                i += 1
            self.addLog('ProgrammeList::setProgrammeStop', 'exit_function')
        except:
            self.addLog('ProgrammeList::setProgrammeStop', 'ERROR: (' + repr(e) + ')', logErorr)

    def getXml(self, xmldoc, node):
        try:
            self.addLog('ProgrammeList::getXml', 'enter_function')
            for prg in self._data:
                prg.getXml(xmldoc, node)
            self.addLog('ProgrammeList::getXml', 'exit_function')
        except Exception as e:
            self.addLog('ProgrammeList::getXml', 'ERROR: (' + repr(e) + ')', logErorr)

    def getProgrammeForUrl(self, url):
        try:
            self.addLog('ProgrammeList::getProgrammeForUrl', 'enter_function')
            for prg in self._data:
                if prg._urlDesc == url:
                    self.addLog('ProgrammeList::getProgrammeForUrl', '*FOUND* exit_function')
                    return prg
            self.addLog('ProgrammeList::getProgrammeForUrl', '*NO FOUND* exit_function')
            return None
        except Exception as e:
            self.addLog('ProgrammeList::getProgrammeForUrl', 'ERROR: (' + repr(e) + ')', logErorr)
            return None

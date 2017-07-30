# -*- coding: utf-8 -*-

# Импортируем нужные нам библиотеки
import urllib, urllib2, re, sys, os, locale

host = 'http://www.vsetv.com/'
useragent = 'Mozilla/5.0 (Windows NT 6.1; rv:5.0) Gecko/20100101 Firefox/5.0'
contenttype = 'application/x-www-form-urlencoded'

# Функция для получения исходного кода web-страниц
def GetHTML(url):
    request = urllib2.Request(url)
    request.add_header('User-Agent', useragent)
    request.add_header('Content-Type', contenttype)
    conn = urllib2.urlopen(request)
    html = conn.read()
    conn.close()

    return html

def remove_tags(vstr):
    rstr = re.sub('<([^!>]([^>]|\n)*)>', '', vstr).strip('&nbsp;').strip(' \t\n\r')
    return rstr

def parse_strings(vstr, vbegin, vend, vrtags=0): 
    idx_beg = vstr.find(vbegin)
    idx_end = vstr.find(vend)
    rstr = vstr[idx_beg:idx_end]
    if vrtags == 1:
        rstr = remove_tags(rstr)
    return rstr

# Тест на работоспособность
encoding = locale.getpreferredencoding(do_setlocale=True)
reload(sys)
sys.setdefaultencoding(encoding)

lang = 'ru'
full_desc = 'false'
type_test = 2

if type_test == 1:
    # channels
    html = GetHTML(host+'channels.html')
    html = html.decode('windows-1251').encode('utf-8')
    data = re.compile('<option value=channel_(.+?)>(.+?)</option>').findall(html)

    for index,oname in data:
        if lang == 'ru':
            flag = oname.find('(на укр.)') == -1
        else:
            flag = oname.find('(на укр.)') != -1
        if flag:
            icon = host + 'pic/channel_logos/' + index + '.gif'
            print index + ';' + oname.decode('utf-8') + ';' + icon
elif type_test == 2:
    # programme
    #html = GetHTML(host+'schedule_channel_5_day_2015-08-31.html')
    html = GetHTML(host+'schedule_channel_237_day_2015-08-31.html')    
    html = html.decode('windows-1251').encode('utf-8')
    if full_desc == 'true':
        data = re.compile('<div class="(?:pasttime|onair|time)">(.+?)</div><div class="(?:pastprname2|prname2)">(.+?)</div>').findall(html)
        for time, title in data:
            url = ''
            idx_beg = title.find('<a href=')
            if idx_beg != -1:
                idx_end = title.find('.html')
                url = title[idx_beg+8:idx_end]+'.html'
            prtitle = remove_tags(title)            
            if url != '':
                print time + ';' + prtitle.decode('utf-8') + ';' + url
            else:
                print time + ';' + prtitle.decode('utf-8')

    else:
        data = re.compile('<div class="(?:pasttime|onair|time)">(.+?)</div><div class="(?:pastprname2|prname2)">(.+?)(?:</div><div id=desc\d{16} class="(?:pastdesc|prdesc)"><div class="desc"><b>(.+?)</div></div>|</div>)').findall(html)
        for time, title, desc in data:
            prtitle = remove_tags(title)
            if desc != '':
                prdesc = remove_tags(desc)
                print time + ';' + prtitle.decode('utf-8') + ';' + prdesc.decode('utf-8')
            else:
                print time + ';' + prtitle.decode('utf-8')    
elif type_test == 3:
    # full desc
    #html = GetHTML(host+'show_81.html')
    html = GetHTML(host+'film_28868.html')
    html = html.decode('windows-1251').encode('utf-8')

    showname = '<td colspan="2" valign="top" class="showname">'
    showmain = '<td width="700" valign="top" class="showmain">'

    showname1 = parse_strings(html,showname,showmain)

    if showname1.find('<strong>') != -1:
        ctmp = parse_strings(showname1,'<br>','<strong>',1).strip(',')
    else:
        ctmp = parse_strings(showname1,'<br>','<!--',1).strip(',').replace('&nbsp;','')

    ccountry = ''
    cdate = ''

    if len(ctmp.split(','))==2:
        ccountry = ctmp.split(',')[0].strip()
        cdate = ctmp.split(',')[1].strip()
        if cdate[-1] == '-':
            cdate = cdate[:-1]
        if cdate != '':
            ctmp = ccountry + ', ' + cdate

    print ctmp.decode('utf-8').strip(' \t\n\r')

    cgenre = ''
    cgenre = parse_strings(showname1,'<strong>','</strong>',1).replace(' / ', ',')
    if cgenre != '':
        print cgenre.decode('utf-8').strip(' \t\n\r').capitalize()

    cdirectors = ''
    cactors = ''
    cdesc = ''

    showmain1 = parse_strings(html,showmain,'<td valign="top">')

    cdirectors = parse_strings(showmain1,'Режиссер(ы):','<br>',1)
    if cdirectors != '':
        cdirectors = cdirectors.decode('utf-8')[12:].strip().strip(' \t\n\r')
        print cdirectors

    cactors = parse_strings(showmain1,'Актеры:','<div>',1)
    if cactors != '':
        cactors = cactors.decode('utf-8')[7:].strip().strip(' \t\n\r') 
        print cactors

    cdesc = parse_strings(showmain1,'<span class="big">','<span class="name">',1)
    if ctmp !='':
        print ctmp.decode('utf-8').strip(' \t\n\r') + '. ' + cdesc.decode('utf-8').strip().strip(' \t\n\r')
    else:
        print cdesc.decode('utf-8').strip().strip(' \t\n\r')

    cstarrating = parse_strings(showmain1,'<span class="name">','Проголосовало',1)
    print cstarrating.decode('utf-8').split(':')[1].strip().strip(' \t\n\r')

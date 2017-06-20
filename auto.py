#!/usr/bin/python
#-*- coding: UTF-8 -*-

import urllib2
import urllib
import cookielib
import json
import requests
import time
import os.path

url_login="https://login.xiami.com/member/login"
AGENT= 'Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/28.0.1500.95 Safari/537.36'
headers = {'User-Agent':AGENT}
cj = cookielib.CookieJar()
url_recommend="http://www.xiami.com/song/playlist/id/1/type/9/cat/json"
url_mess = 'http://www.xiami.com/song/playlist/id/%s/type/0/cat/json'
local_download_path = ''
email=''
password=''

def init():
    global email, password,local_download_path
    print "init"
    f = open("account")
    email = f.readline().strip()
    password = f.readline().strip()
    local_download_path = f.readline()
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
    urllib2.install_opener(opener)
    currentDay = time.strftime("%Y-%m-%d", time.localtime())
    local_download_path = local_download_path + currentDay + '/'
    print 'create dir:', local_download_path
    if os.path.isdir(local_download_path):
        pass
    else:
        os.makedirs(local_download_path)

def login():
    print "start login"
    form = {'email':email, 'password':password, 'submit':'登 录'}
    form_encode  = urllib.urlencode(form)
    headers['Referer'] = url_login
    request = urllib2.Request(url_login, form_encode, headers)
    response = urllib2.urlopen(request)
    for cookie in enumerate(cj):
        print cookie[1].name, urllib.unquote(cookie[1].value)
        
def getRecommend():
    print 'getRecommend'
    headers['Referer'] = url_recommend
    request = urllib2.Request(url_recommend, headers=headers)
    response = urllib2.urlopen(request)
    return response.read()


def decode_xiami_link(mess):
    """decode xm song link"""
    rows = int(mess[0])
    url = mess[1:]
    len_url = len(url)
    cols = len_url / rows
    re_col = len_url % rows # how many rows need to extend 1 col for the remainder
    
#     for row in range(rows+1):
#         print url[row*(cols+1):row*(cols+1)+cols+1]
     
    l = []
    for row in xrange(rows):
        ln = cols + 1 if row < re_col else cols
        l.append(url[:ln])
        url = url[ln:]
     
    durl = ''
    for i in xrange(len_url):
        durl += l[i%rows][i/rows]
     
    return urllib.unquote(durl).replace('^', '0')
    
def parseSongs(jsonStr):
#     print 'parse songs', jsonStr
    songs = json.loads(jsonStr)
    print type(songs['data']['trackList'])
    for song in songs['data']['trackList']:
        song_info_url=url_mess%song['songId']
#         print song_info_url
        request = urllib2.Request(song_info_url, headers=headers)
        response = urllib2.urlopen(request)
        result=response.read()
        songInfo = json.loads(result)
        songname = songInfo['data']['trackList'][0]['songName']
        download_url = decode_xiami_link(songInfo['data']['trackList'][0]['location'])
        print'------------------------------------------------------------------------------------------------------------------------'
        print songname
        print download_url
        print'------------------------------------------------------------------------------------------------------------------------'
        download(songname, download_url)
#         download_with_timeout(songname, download_url, 60)
        
        
def download(songname, url):
    songname = songname.replace(u"/", " ")
    localfile=local_download_path+songname+".mp3"
    print "download ", songname, ' from ', url, ' to ', localfile
    request = urllib2.Request(url)
    response = urllib2.urlopen(request)
    data = response.read()
    with open(localfile, "wb") as code:
        code.write(data)
        
# class TooSlowException(Exception):
#     print 'TooSlowException happen'
#         
# def download_with_timeout(songname, url, timeout):
#     print 'download_with_timeout'
#     startTime = time.time()
#     localfile = local_download_path+songname+'.mp3'
#     f = open(localfile, 'wb')
#     request = requests.get(url, stream=True)
#     for chunk in request.iter_content(chunk_size=65536):
#         if chunk:
#             nowTime = time.time()
#             if (nowTime - startTime > timeout):
#                 raise TooSlowException
#             startTime = nowTime
#             f.write(chunk)
#             f.flush()
#     f.close()
                
            

if __name__ == '__main__':
    print "auto download daily music"
    init()
    login()
    jsonStr = getRecommend()
    parseSongs(jsonStr)

















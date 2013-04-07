# coding: utf-8
__author__ = 'Snake'
import urllib, urllib2, json, cookielib, os
import eyeD3
from BeautifulSoup import BeautifulSoup


songs_dir = 'songs'
base_url = 'http://douban.fm/j/mine/playlist?type=n&sid=&pt=0.0&channel=0&from=mainsite'
songinfo_url = 'http://dbfmdb.sinaapp.com/api/song.php?sid=%s'
song_url = 'http://douban.fm?start=%sg%sg'
invalid = ['/', '\\', ':', '*', '?', '"', '<', '>', '|']
first_url = 'http://douban.fm/mine?start=%d&type=liked'
base_header = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; rv:20.0) Gecko/20100101 Firefox/20.0'}


#验证文件名是否符合规范
def valid_filename(s):
    #lambda表达式定义一个函数 s当作一个序列里面每一个字符都和invalid对比如果不在里面的就返回true
    #filter函数是将s内符合lambda表达式结果返回一个新的字符串
    return filter(lambda x: x not in invalid, s)


#获取歌曲的信息和下载地址
def get_song_information(sid):
    detail = json.loads(get_url_result(songinfo_url % sid))
    if detail:
        get_url_result(song_url % (sid, detail['ssid']))
        result = get_url_result(base_url)
        ret = json.loads(result)
        return ret['song'][0]
    else:
        return


#获取歌曲
def get_songs(url, cookie):
    content = get_url_result(url, cookie)
    soup = BeautifulSoup(str(content))
    for div in soup.findAll('div', {'class': 'info_wrapper'}):
        sid = div.find('div', {'class': 'action'})['sid']
        song = get_song_information(sid)
        if song:
            download_song(song)
        else:
            pass


#根据url和cookie获取网页内容
#如果传入cookie不为空那么将通过cookie的方式获取url信息
#如果传入的cookie为空那么就已普通的方式过去url信息
def get_url_result(url, cookie=None):
    headers = base_header
    headers['Referer'] = url
    if cookie:
        headers['Cookie'] = cookie
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookielib.CookieJar()))
        urllib2.install_opener(opener)
    req = urllib2.Request(url=url, headers=headers)
    try:
        content = urllib2.urlopen(req, timeout=20).read()
        return content
    except  Exception as e:
        print e.message + '\n'


#下载歌曲并且根据歌曲信息完善mp3的tag信息
def download_song(song):
    try:
        os.mkdir(songs_dir)
    except  Exception as e:
        print e.message + '\n'
        pass
    filename = '%s-%s.mp3' % (valid_filename(song['artist']), valid_filename(song['title']))
    print "download %s" % filename
    filepath = os.path.join(songs_dir, filename)
    if os.path.exists(filepath):
        return
    urllib.urlretrieve(song['url'], filepath)
    picname = filename.replace('.mp3', '.jpg')
    picpath = os.path.join(songs_dir, picname)
    urllib.urlretrieve(song['picture'].replace('mpic', 'lpic'), picpath)
    tag = eyeD3.Tag()
    tag.link(filepath)
    tag.header.setVersion(eyeD3.ID3_V2_3)
    tag.encoding = '\x01'
    tag.setTitle(song['title'])
    tag.setAlbum(song['albumtitle'])
    tag.setArtist(song['artist'])
    tag.setDate(song['public_time'])
    tag.addImage(3, picpath)
    os.remove(picpath)
    tag.update()


def main():
    cookie = raw_input("cookie: ")
    print 'you should enter the pages you want to download'
    page0 = int(raw_input("page from: "))
    page1 = int(raw_input("page to: "))
    for i in range(page1 - page0 + 1):
        get_songs(first_url % ((i + page0 - 1) * 15), cookie)

if __name__ == '__main__':
    main()
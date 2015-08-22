#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2015-08-14 17:15:47
# @Author  : zhouwei
# @Version : $Id$

from __future__ import division, absolute_import, unicode_literals, print_function
import re
import sys
from urllib2 import Request, urlopen, URLError, HTTPError, unquote
from urllib2 import install_opener, HTTPHandler, HTTPSHandler, build_opener
from urlparse import urlparse


def usage():
    '''usage'''
    print("\nThis is the usage function\n")
    print('Usage: '+sys.argv[0]+' <url>')


def fetch_url(url):
    '''获取播放url'''
    req = Request(url)
    try:
        response = urlopen(req)
        html = response.read()
        # print(html)
    except URLError as e:
        print("Reason: ", e.reason)
    except HTTPError as e:
        print('Http Error code: ', e.code)
    else:
        match = re.search(r'(?<=flashvars="list=).+?(?=" \/>)', html)
        url = ''
        if match:
            url = match.group(0)
            url = unquote(url)
        print(url)

        return url


def debug():
    '''debug'''
    httpHandler = HTTPHandler(debuglevel=1)
    httpsHandler = HTTPSHandler(debuglevel=1)
    opener = build_opener(httpHandler, httpsHandler)
    install_opener(opener)


def fetch_m3u8(url):
    '''提取m3u8文件, 方法播放列表!'''
    req = Request(url)
    try:
        response = urlopen(req)
        html = response.read()
    except URLError as e:
        raise e
    except HTTPError as e:
        raise e
    else:
        return parse_m3u8(html)


def parse_m3u8(contents):
    playlist = contents.split('\n')
    print('----------------')
    # m = [x for x in m if '#EXT' not in x]
    for i in range(len(playlist)-1, -1, -1):
        if '#EXT' in playlist[i]:
            del playlist[i]
        else:
            if playlist[i].find('?') > 0:
                playlist[i] = playlist[i][0:playlist[i].find('?')]

    return playlist


def download(url):
    ''' download function'''
    file_name = url.split('/')[-1]
    u = urlopen(url)
    meta = u.info()
    file_size = int(meta.getheaders("Content-Length")[0])
    print("Downloading: %s Bytes: %s" % (file_name, file_size))
    block_size = 8192
    file_size_dl = 0

    with open(file_name, 'wb') as f:
        while True:
            readbuffer = u.read(block_size)
            if not readbuffer:
                break

            file_size_dl += len(readbuffer)
            f.write(readbuffer)
            status = r"%10d  [%3.2f%%]" % (file_size_dl, file_size_dl * 100. / file_size)
            status = status + chr(8)*(len(status)+1)
            # print(status),
            sys.stdout.write(status)
            sys.stdout.flush()


def fetch_video(url):
    '''提取微博视频'''
    videourl = fetch_url(url)
    m3u8uri = urlparse(videourl)
    print(m3u8uri)

    playlist = fetch_m3u8(videourl)
    for item in playlist:
        simple_url = m3u8uri.scheme + "://" + m3u8uri.netloc + "/" + item
        print(simple_url)
        download(simple_url)


def check_url(url):
    '''检查输入url'''
    checked = False
    match = re.search(r"^http?://video.weibo.com/show\?fid=\w+", url)
    if match:
        checked = True

    return checked


def main():
    '''
    main function
    '''
    if len(sys.argv) < 2:
        print("No url specified:")
        usage()
        sys.exit()

    # url = "http://video.weibo.com/show?fid=1034:2bdc384e8c624de0a7f2b1a4d9685876"
    # url = "http://www.baidu.com"
    url = sys.argv[1]

    if check_url(url):
        fetch_video(url)
    else:
        print("url format error")
    # print(check_url(url))


if __name__ == '__main__':
    main()

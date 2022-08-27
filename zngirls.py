# coding:utf-8
from __future__ import print_function
import multiprocessing
from bs4 import BeautifulSoup
import os
import time
import requests
import sys
import eventlet


reload(sys)
sys.setdefaultencoding('utf8')

HOST = "www.fnvshen.com"
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36',
    # 'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
    # 'Accept-Encoding':'gzip, deflate, br',
    # 'Accept-Language':'zh-CN,zh;q=0.9,en;q=0.8',
    # 'Cache-Control':'max-age=0',
    # 'Connection' : 'keep-alive',
    # 'Sec-Fetch-Mode': 'navigate',
    # 'Sec-Fetch-Site': 'none',
    # 'Sec-Fetch-User': '?1',
    # 'Upgrade-Insecure-Requests':'1',
    'Referer': "https://{}".format(HOST),
    'sec-ch-ua': '" Not;A Brand";v="99", "Google Chrome";v="91", "Chromium";v="91"',
    'sec-ch-ua-mobile': '?0',
}


def getHtmlSoup(url):
    headers = HEADERS
    pre_fix = "https://{}/img.html?img=".format(HOST)
    headers.update({
        'Referer': pre_fix + url
    })
    respost = requests.post(url=url, headers=headers)
    webdata = requests.get(url=url, headers=headers, cookies=respost.cookies)
    html = webdata.text
    Soup = BeautifulSoup(html, 'lxml')

    return Soup, html


def getpic(url, target):
    headers = HEADERS

    try:
        # print('11111111111')
        respost = requests.post(url=url, headers=headers)
        # print('22222222222')
        respose = requests.get(url=url, headers=headers, cookies=respost.cookies, stream=True)
    except requests.exceptions:
        print('图片无法下载')
        respose = requests.get(url=url, headers=headers, cookies=respost.cookies, stream=True)

    image = respose.content
    with open(target, "wb") as jpgfile:
        jpgfile.write(image)
    print("下载完成%s" % (target))
    jpgfile.close()


def getnextpage(url, URL):
    '''http://www.zngirls.com/g/18666/2.html'''
    Soup, Html = getHtmlSoup(url)

    nexttags = Soup.select('#pages > a')
    postfix = nexttags[-1].get('href')

    homeurl = 'https://' + HOST
    nextpage = homeurl + postfix
    firstpage = URL[:-1]

    if not (nextpage == firstpage):
        print(nextpage)
        return nextpage
    else:
        return False


def getAllpage(url, URL):
    pagelist = [URL]
    nexturl = getnextpage(url, URL)
    while nexturl:
        pagelist.append(nexturl)
        nexturl = getnextpage(nexturl, URL)
    return pagelist


def high_resolution_url_translation(url):
    trans_url = url.replace('/s/', '/')
    return trans_url


def getEachPageOriginalImageURL(url):
    Soup, Html = getHtmlSoup(url)
    imageinfo = []
    imagetags = Soup.select('#hgallery > img')
    # print(imagetags)
    for src, filename in zip(imagetags, imagetags):
        data = {
            'src': high_resolution_url_translation(src.get('src')),
            'filename': filename.get('alt')
        }
        # print(data)
        imageinfo.append(data)

    return imageinfo


def getFoldername(url):
    Soup, Html = getHtmlSoup(url)
    foldernametag = Soup.select('#htilte')
    foldername = foldernametag[0].get_text()
    return foldername


def DownloadImage(url, foldername, pagenumber):
    ImageInfolist = getEachPageOriginalImageURL(url)
    photocount = 0

    for info in ImageInfolist:
        src = info['src']
        filename = info['filename']
        # print(src,filename)
        path = '/Users/sparrow/Downloads/ZNgirls/%s/' % foldername

        if not os.path.exists(path):
            os.makedirs(path)

        target = path + '%s.jpg' % filename

        print("正在下载图片%s" % (target))
        # time.sleep(0.5)

        eventlet.monkey_patch()  # 必须加这条代码
        with eventlet.Timeout(15, False):  # 设置超时时间为10秒
            getpic(src, target)
            photocount += 1

        # urllib.urlretrieve(src, target)


    print("--------------------------------------------------\n"
          "第%s页下载完成,进程ID:%s\n"
          "--------------------------------------------------\n" % (pagenumber + 1, os.getpid()))

    countQueue.put(photocount)


def Download(url, URL):
    print("正在读取相册片信息...")
    Foldername = getFoldername(url)
    Pageurllist = getAllpage(url, URL)
    Pagenumber = len(Pageurllist)

    count = []

    global countQueue
    manager = multiprocessing.Manager()
    countQueue = manager.Queue()

    downloadphoto = multiProcess(DownloadImage, Pageurllist, Pagenumber)
    downloadphoto.downloadworks(Foldername)

    # 从查找页面的所有进程中通过进程通信queue获得每一页的图片
    for i in range(Pagenumber):
        count.append(i)
        count[i] = 0
        count[i] += countQueue.get(True)

    print("这个相册有 %s 张图片" % count)


class multiProcess(multiprocessing.Process):
    """docstring for multiProcess"""

    def __init__(self, func, arg, worknum):
        super(multiProcess, self).__init__()
        self.func = func
        self.arg = arg
        self.worknum = worknum

    def downloadworks(self, foldername):
        # p = multiprocessing.Pool(self.worknum) # 由于作了反爬虫限频，不能同时开启过多线程
        p = multiprocessing.Pool(10)
        for i in range(self.worknum):
            page_url = self.arg[i]
            p.apply_async(self.func, args=(page_url, foldername, (i + 1)))

        p.close()
        p.join()


if __name__ == '__main__':
    t0 = time.time()
    print('''
		---------------------------------
		      欢迎使用相册批量下载器
		---------------------------------
		Author:  Sparrow
  		Created: 2016-7.22
  		Email: sparrow629@163.com
	''')

    chose_quit = 'Y'
    while not chose_quit == 'N':
        url = raw_input("请粘贴URL于此:")
        Download(url, url)
        print(time.time() - t0)
        chose_quit = raw_input('\n继续选择下载请按键[Y],退出请按键[N]:')

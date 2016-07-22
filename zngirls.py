#coding:utf-8
from __future__ import print_function
from multiprocessing import Pool
import multiprocessing
from bs4 import BeautifulSoup
import os, time, random, urllib
import requests
import sys
reload(sys)
sys.setdefaultencoding('utf8')

def getHtmlSoup(url):
	headers = {
		'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36',
		'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
		'Accept-Encoding':'gzip, deflate, sdch',
		'Accept-Language':'zh-CN,zh;q=0.8,en;q=0.6',
		'Cache-Control':'max-age=0',
		'Connection' : 'keep-alive',
		'Upgrade-Insecure-Requests':'1'
			}
	respost = requests.post(url=url, headers = headers)
	webdata = requests.get(url = url, headers = headers, cookies = respost.cookies)

	html = webdata.text
	Soup = BeautifulSoup(html, 'lxml')
	# print(Soup)
	return Soup

def getpic(url,target):
	headers = {
		'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36',
		'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
		'Accept-Encoding':'gzip, deflate, sdch',
		'Accept-Language':'zh-CN,zh;q=0.8,en;q=0.6',
		'Cache-Control':'max-age=0',
		'Connection' : 'keep-alive',
		'Upgrade-Insecure-Requests':'1',
		'Referer':url
	}
	respost = requests.post(url=url, headers=headers)
	respose = requests.get(url=url, headers=headers, cookies=respost.cookies, stream = True)

	image = respose.content

	with open(target, "wb") as jpgfile:
		jpgfile.write(image)
	# print(jpgfile)
	jpgfile.close()


def getnextpage(url, URL):
	'''http://www.zngirls.com/g/18666/2.html'''
	Soup = getHtmlSoup(url)
	
	nexttags = Soup.select('#pages > a')
	postfix = nexttags[-1].get('href')
	
	homeurl = 'http://www.zngirls.com'
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
		nexturl = getnextpage(nexturl,URL)
	return pagelist

def getEachPageOriginalImageURL(url):
	Soup = getHtmlSoup(url)
	imageinfo = []
	imagetags = Soup.select('#hgallery > img')
	# print(imagetags)
	for src,filename in zip(imagetags,imagetags):
		data = {
		'src': src.get('src'),
		'filename': filename.get('alt')
		}
		# print(data)
		imageinfo.append(data)

	return imageinfo

def getFoldername(url):
	Soup = getHtmlSoup(url)
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
		path = 'ZNgirls/%s/' % foldername

		if not os.path.exists(path):
			os.makedirs(path)

		target = path + '%s.jpg' % filename
		
		print("正在下载图片%s" % (target))
		getpic(src,target)

		# urllib.urlretrieve(src, target)


		photocount +=1

	print("--------------------------------------------------\n"
			  "第%s页下载完成,进程ID:%s\n"
			  "--------------------------------------------------\n" % (pagenumber + 1, os.getpid()))

	countQueue.put(photocount)


def Download(url,URL):

	print("正在读取相册片信息...")
	Foldername = getFoldername(url)
	Pageurllist = getAllpage(url,URL)
	Pagenumber = len(Pageurllist)

	count = 0

	global countQueue
	manager = multiprocessing.Manager()
	countQueue = manager.Queue()

	downloadphoto = multiProcess(DownloadImage, Pageurllist ,Pagenumber )
	downloadphoto.downloadworks(Foldername)

	# 从查找页面的所有进程中通过进程通信queue获得每一页的图片
	for i in range(Pagenumber):
		count += countQueue.get(True)

	print("这个相册有 %s 张图片" % count)

class multiProcess(multiprocessing.Process):
	"""docstring for multiProcess"""
	def __init__(self, func, arg, worknum):
		super(multiProcess, self).__init__()
		self.func = func
		self.arg = arg
		self.worknum = worknum

	def downloadworks(self, foldername):
		p = multiprocessing.Pool(self.worknum)
		for i in range(self.worknum):
			page_url = self.arg[i]
			p.apply_async( self.func, args = (page_url,foldername,(i + 1)))

		p.close()
		p.join()


if __name__ == '__main__':
	# # url = 'http://www.zngirls.com/g/18666/'
	# url = 'http://t1.zngirls.com/gallery/20440/18666/009.jpg'
	# filename = 'filename'
	# # print(src,filename)
	# path = 'ZNgirls/test/'
	#
	# if not os.path.exists(path):
	# 	os.makedirs(path)
	#
	# target = path + '%s.jpg' % filename
	# getpic(url, target)
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
		Download(url,url)
		chose_quit = raw_input('\n继续选择下载请按键[Y],退出请按键[N]:')



	print(time.time()-t0)
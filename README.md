# Crawler_image_zngirls
This is a multiprocessing clawer for images

# Problem
经过前面三个爬虫的联系，基本上已经解决了所有爬虫技术上的难题。
1.这个网站看起来有点野，但是做了相当足的反爬虫措施，必须伪装成浏览器行为post之后得到cookie再请求每一页，才能正常打开网页，个人觉得比封ip强多了，于是，添加了headers。
####但是这一次遇到了两个新的问题：
2.一个问题，http://www.zngirls.com/ 这个网站有图片反盗链防护。
解释一下，图片反盗链就是就是，如果没有带refer的直接访问图片的连接，会被视为是在盗链，会触发脚本，自动用其他图片代替你在下的图片。但是我之前所有下载图片都是使用urllib.urlretrieve,不知道怎么添加refer进行访问啊。
于是我改进了，马上想到了request，于是就模仿浏览器行为，加refer直接得到图片的内容写入文件夹。这一次畅通无阻。
同时也涨了不少姿势。

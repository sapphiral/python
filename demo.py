import os
import re
import requests
import time

class A:
	def __init__(self,url):
		self.baseUrl = url
		self.basePath=os.getcwd().replace("\\","/")
		self.currentUrl = url
		self.currentPath=os.getcwd()
		self.req = requests.Session()
		self.text = self.req.get(url).text.replace("\r","")
		self.collection =[]
		self.a = self.getLinka(0)
		self.css = self.getLinkcss(0)
		self.js = self.getLinkjs(0)
		self.img = self.getLinkimg()

	# split get link for scalability
	def getLinka(self,times):
		a=re.findall(r"<a[^>]*?>",self.text)
		a_href = [re.findall(r"href=[\"\'](.*?)[\"\']",i)[0] for i in a]
		#how many times you want getLinka goes deeper?
		#be careful!
		while times > 0:
			a_href += self.getLinka(times-1)
		a_href=list(set(a_href))
		for url in a_href:
			if "javascript:void(0)" in url:
				a_href.remove(url)
			elif "#" in url:
				a_href.remove(url)
			elif self.isAbsPath(url):
				a_href.remove(url)

		return a_href

	def getLinkcss(self,times):
		link_href = re.findall(r"<link.*href\s*=\s*[\"\'].*?(.*?)[\"\']",self.text)
		style_url = re.findall(r"url\s*\([\'\"].*?(.*?)[\'\"]\)",self.text,re.DOTALL)
		#how many times you want getLinkcss goes deeper?
		#strictly should be 1 only
		while times > 0:
			link_href += self.getLinkcss(times-1)
		return list(set(link_href)) + list(set(style_url))

	def getLinkjs(self,times):
			#how many times you want getLinkjs goes deeper?
		#strictly should be 1 only
		script_src = re.findall(r"<script.*src\s*=\s*[\'\"].*?(.*?)[\'\"]",self.text)
		while times > 0:
			a_href += self.getLinka(times-1)
		return list(set(script_src))
	def getLinkimg(self):
		img = re.findall(r"<img.*src\s*=\s*[\'\"].*?(.*?)[\'\"]",self.text)
		return list(set(img))
	def getLinkiframe(self):
		iframe = re.findall(r"<iframe.*src\s*=\s*[\'\"].*?(.*?)[\'\"]",self.text)
		return list(set(iframe))
	def getLinkvideo(self):
		video = re.findall(r"<video.*?</video>",a.text,re.DOTALL)
		video_src = []
		for i in video:
			video_src += re.findall(r"src\s*=\s*[\'\"](.*?)[\'\"]",i,re.DOTALL)
		return list(set(video_src))
	def getLinkaudio(self):
		audio = re.findall(r"<audio.*?</audio>",a.text,re.DOTALL)
		audio_src = []
		for i in video:
			video_src += re.findall(r"src\s*=\s*[\'\"](.*?)[\'\"]",i,re.DOTALL)
		return list(set(audio_src))
	def run(self):
		start=time.time()
		self.download(self.baseUrl,0)
		while len(self.css) > 0:
			url = self.css.pop()
			self.download(url,"css")
		while len(self.js) > 0:
			url = self.js.pop()
			self.download(url,"js")
		print("Finished in: ",time.time()-start)
	def download(self,url,flag):
		fullUrl = self.parse_url(url)
		computerPath = self.parse_path(fullUrl,flag)
		if os.path.isfile(computerPath):
			return None
		# turn the link to full http link to download
		downloadedContent=self.req.get(fullUrl)
		##full_path to be written to computer file
		if not os.path.dirname(computerPath):
			pass
		else:
			os.makedirs(os.path.dirname(computerPath),exist_ok=True)
		if self.isByteEncoding(computerPath):
			print("no", url)
			with open(computerPath,"wb") as f:
				f.write(downloadedContent.content)
		else:
			## change html [link] path relative to main path
			content = self.parse_content(downloadedContent.text)
			print("yes")
			with open(computerPath,"w") as f:
				f.write(content)
	def parse_content(self,content):
		content = content.replace("\r","")
		# a = self.getLinka()
		for _url in self.css:
			__url = self.parse_path(self.parse_url(_url),"css")
			content = content.replace(_url,__url)

		for _url in self.js:
			__url = self.parse_path(self.parse_url(_url),"js")
			content = content.replace(_url,__url)
		# for _url in a:
			# pass
		return content
	def parse_url(self,url):
		#case1: url is abs path
		if self.isAbsPath(url):
			basePath = os.path.basename(url).replace("www.","")
			if basePath[-1]=="/":
				basePath = basePath[:-1]
			if len(url)<=2 or basePath in self.baseUrl:
				return self.baseUrl
			if url[:2]=="//":
				return "https:"+url
			return url
		#case2: url is rel path
		if url[:2]=="./":
			url = url[1:]
		if url[0]=="/":
			return self.baseUrl+"/"+\
			url[1:]
		#case3: url is base path
		if "../" in url:
			_path = ""
			if self.currentUrl == self.baseUrl:
				_path = self.baseUrl
			else:
				_path=""
				for i in re.findall(r"\.\./",url):
					_path = os.path.dirname(self.currentUrl)
					if _path == self.baseUrl:
						break
			url = url.replace("../","")
			return _path+"/"+url
		return self.currentUrl + "/" + url
	def parse_path(self,url,flag):
		if self.baseUrl in url:
			url = url.replace(self.baseUrl,"")
		basePath=os.path.basename(url)
		dirPath = url.replace(basePath,"")
		if flag=="a":
			basePath = basePath.replace(re.findall(r"\.\w+",basePath)[0],".html")
			url = dirPath+re.findall(r"[^/]+\.\w+",basePath)[0]
			return url[1:]
		# if file is css
		elif flag=="css":
			url = dirPath+re.findall(r"[^/]+\.\w+",basePath)[0]
			if self.isAbsPath(url):
				return os.path.basename(url)
			return url[1:]
		elif flag=="js":
			url = dirPath+re.findall(r"[^/]+\.js",basePath)[0]
			if self.isAbsPath(url):
				return os.path.basename(url)
			return url[1:]
		else:
			return self.basePath+"/"+"index.html" #1
	def isByteEncoding(self,computerPath):
		# include images or fonts format
		ext = re.findall(r"\.(\w+)",computerPath)[-1]
		if ext not in ['css','js','asp','html','htm']:
			return True
	def isAbsPath(self,url):
		if ('http:' in url) or ('https' in url) or ('//' in url) or (url=="/"):
			return True
a = A("https://www.w3schools.com")
a.download(a.baseUrl,0)
# for i in a.a:
#         url=a.parse_url(i)
#         # print(url)
#         print(a.parse_path(url,"a"))

# for i in a.css:
#         url=a.parse_url(i)
#         # print(url)
#         print(a.parse_path(url,"css"))

# for i in a.js:
#         url=a.parse_url(i)
#         # print(url)
#         print(a.parse_path(url,"js"))



a.run()
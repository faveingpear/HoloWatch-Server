import os 
import sys
import json
import time

import webbrowser
import requests
import threading
from bs4 import BeautifulSoup

MEMEBERS_PATH = "members.json"

class HoloLiveMember():

	def __init__(self, name=None, channel_id=None, devision=None, isLive=None,photopath=None,branch=None):
		self.devision = devision
		self.channel_id = channel_id
		self.name = name
		self.isLive = isLive
		self.photoPath = photopath
		self.branch = branch
		self.old_video_id_list = []
		self.videoid = set()

	# def addElements(self, container,x,y, buttontext):

	# 	self.containerWidget = QWidget() #Widget to containe the Hboxlayout

	# 	self.containerBox = QHBoxLayout() #layout so that the pfp a button are right next to eachother

	# 	self.pfplabel = QLabel()
	# 	Pixmap = QPixmap(self.photoPath)
	# 	newPixmap = Pixmap.scaled(64, 64, Qt.KeepAspectRatio)
	# 	self.pfplabel.setPixmap(newPixmap)
	# 	self.pfplabel.resize(64,64)
	# 	self.containerBox.addWidget(self.pfplabel)
		
	# 	self.containerBox.addStretch()

	# 	self.livebutton = QPushButton()
	# 	self.livebutton.clicked.connect(self.openLiveStream)
	# 	self.livebutton.setText(buttontext)
	# 	self.containerBox.addWidget(self.livebutton)

	# 	self.containerWidget.setLayout(self.containerBox)
	# 	container.addWidget(self.containerWidget,x,y)
	
	def getStreamThumbnail(self):
		if self.isLive:
			for videos in self.videoid:
				return "https://i.ytimg.com/vi/" + videos + "/sddefault.jpg"
		else:
			return None

	def openLiveStream(self):
		if self.isLive:
			for videos in self.videoid:
				return "https://www.youtube.com/watch?v=" + videos
				#webbrowser.open("https://www.youtube.com/watch?v=" + videos)
		else:
			return None
	
	# def updateLiveStatus(self, offline=None, live=None):
		
	# 	if self.isLive:
	# 		self.livebutton.setText(live)
	# 	else:
	# 		self.livebutton.setText(offline)

# --- 	
# Thank you so much for this amazing code pusaitou https://github.com/pusaitou/mikochiku_alarm 
# I only slighty changed it to support the class model

	def check_live(self, offline=None, live=None):
		#if sort == self.branch:
		buff_video_id_set = self.get_live_video_id(self.channel_id)
		#print("buff_video_id_set", buff_video_id_set)
		#print("self.old_video_id_list", self.old_video_id_list)
		if buff_video_id_set:
			for getting_video_id in buff_video_id_set:
				if not getting_video_id == "" and not getting_video_id is None:
					if not getting_video_id in self.old_video_id_list:
						self.old_video_id_list.append(getting_video_id)
						if len(self.old_video_id_list) > 30:
							self.old_video_id_list = self.old_video_id_list[1:]

						self.isLive = True
						#self.updateLiveStatus(offline, live)
						print(self.name + " is online: " + str(self.isLive))
						return
		else:
			self.isLive = False
			print(self.name + " is offline")
			
		#self.updateLiveStatus(offline, live)
		#else:
		#	pass
			
	def get_live_video_id(self, search_ch_id):
		dict_str = ""
		video_id_set = set()
		try:
			session = requests.Session()
			headers = {
				'user-agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36'}
			html = session.get("https://www.youtube.com/channel/" +
							   search_ch_id, headers=headers, timeout=10)
			soup = BeautifulSoup(html.text, 'html.parser')
			keyword = 'window["ytInitialData"]'
			for scrp in soup.find_all("script"):
				if keyword in str(scrp):
					dict_str = str(scrp).split(' = ', 1)[1]
			dict_str = dict_str.replace('false', 'False')
			dict_str = dict_str.replace('true', 'True')

			index = dict_str.find("\n")
			dict_str = dict_str[:index-1]
			dics = eval(dict_str)
			for section in dics.get("contents", {}).get("twoColumnBrowseResultsRenderer", {}).get("tabs", {})[0].get("tabRenderer", {}).get("content", {}).get("sectionListRenderer", {}).get("contents", {}):
				for itemsection in section.get("itemSectionRenderer", {}).get("contents", {}):
					items = {}
					if "shelfRenderer" in itemsection:
						for items in itemsection.get("shelfRenderer", {}).get("content", {}).values():
							for item in items.get("items", {}):
								for videoRenderer in item.values():
									for badge in videoRenderer.get("badges", {}):
										if badge.get("metadataBadgeRenderer", {}).get("style", {}) == "BADGE_STYLE_TYPE_LIVE_NOW":
											video_id_set.add(
												videoRenderer.get("videoId", ""))
					elif "channelFeaturedContentRenderer" in itemsection:
						for item in itemsection.get("channelFeaturedContentRenderer", {}).get("items", {}):
							for badge in item.get("videoRenderer", {}).get("badges", {}):
								if badge.get("metadataBadgeRenderer", {}).get("style", "") == "BADGE_STYLE_TYPE_LIVE_NOW":
									video_id_set.add(
										item.get("videoRenderer", {}).get("videoId", ""))
		except:
			return video_id_set
			
		self.videoid = video_id_set
		return video_id_set

def loadMembers():

	memberlist = []

	membersfile = open(MEMEBERS_PATH,"r")

	members = json.load(membersfile)

	#print(members)

	membersfile.close()

	for i in range(len(members)):
		print("Adding " + members[i]['name'] + " " + members[i]['id'] + " " + members[i]["branch"])
		memberlist.append(HoloLiveMember(members[i]['name'],members[i]['id'],"main",False,members[i]["branch"]))

	return memberlist

def updateStatus(list):

	for member in list:
		member.check_live()
		print(member.isLive)

def createUpdateFile(memberlist):

	finaljson = []

	for member in memberlist:

		json = {
			"name": None,
			"status":False,
			"link":None,
			"thumbnail":None
		}

		json['name'] = member.name
		json['status'] = member.isLive
		json['link'] = member.openLiveStream()
		json['thumbnail'] = member.getStreamThumbnail()

		finaljson.append(json)

	return finaljson

def saveJson(data):

	file = open("update.json","w")

	json.dump(data,file,ensure_ascii = False, indent=4)

	file.close()

membersList = loadMembers()
updateStatus(membersList)
updateJson = createUpdateFile(membersList)
saveJson(updateJson)

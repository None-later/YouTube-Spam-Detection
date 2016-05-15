from multiprocessing import Pool, Lock, Queue, Manager
import sys
from time import sleep
from sys import argv
from apiclient.discovery import build
from apiclient.errors import HttpError
from oauth2client.tools import argparser
import gzip, json
import os.path

DEVELOPER_KEY = ["AIzaSyABDLbZVLdQIiEkbHCffNnK4cXA-xDBeEQ","AIzaSyBhErLc8toAd3f0OgOg-WjV1gonI1FrrfM"]
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

#grep -ro "channelId[^,]*" . | cut -d':' -f3 | sed s/..// | sed s/\"//
ChannelFolder = "../data/ChannelDetails/"
VideoFolder = "../data/VideoDetails/"
def get_channelInfo(channel_id):
	results = ""
	x = 0
	while(x == 0):
		for keys in DEVELOPER_KEY:
			try:
				youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,developerKey=keys)
				x = 1
				break
			except:
				if(keys == DEVELOPER_KEY[-1]):
					sleep(5)
				x = 0
	try:
		results = youtube.channels().list(
		part="brandingSettings,localizations,snippet,contentDetails,contentOwnerDetails,statistics",
		id=channel_id
		).execute()
	except Exception,e:
		print "exception:",e,"channedId:",channel_id
	return results

def new_process(videoid,output):
	channel_id = 0
	t={}
	with open(VideoFolder+"Video_"+videoid+".json") as f:
		t = json.load(f)
	try:
		channel_id = t["items"][0]["snippet"]["channelId"].strip().encode("utf-8")
		info = get_channelInfo(channel_id)
	except Exception,e:
		print "exception:",e,"channedId:",channel_id
		output.put(videoid)
	if info != "":
		with open( ChannelFolder + "Video_" + videoid + ".json", mode ="wt" ) as f:
				json.dump(info,f)

#Call Code as python getChannelDetails.py <videoidfile>

if __name__ == '__main__':
	vid_list=list()
	pool = Pool(processes = 3)
	mgr = Manager()
	result_queue = mgr.Queue()
	with open(argv[1]) as f:
		vid_list = f.readlines()
	for videoid in vid_list:
		if os.path.isfile(ChannelFolder+"Video_"+videoid.strip()+".json") == False:
			print videoid.strip()
			pool.apply_async(new_process, (videoid.strip(), result_queue))
	pool.close()
	pool.join()
	failed_id=[]
	while not result_queue.empty():
		failed_id += [result_queue.get()]
	with open("../data/failed_id_getChannelDetails.txt",mode="w+") as f:
		f.write('\n'.join(failed_id))

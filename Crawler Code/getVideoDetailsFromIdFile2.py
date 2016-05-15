#!/usr/bin/python
import sys
import os
from time import sleep
from sys import argv
from apiclient.discovery import build
from apiclient.errors import HttpError
from oauth2client.tools import argparser
from multiprocessing import Pool, Lock, Queue, Manager
import json


# Set DEVELOPER_KEY to the API key value from the APIs & auth > Registered apps
# tab of
#   https://cloud.google.com/console
# Please ensure that you have enabled the YouTube Data API for your project.
DEVELOPER_KEY = ["AIzaSyABDLbZVLdQIiEkbHCffNnK4cXA-xDBeEQ","AIzaSyBhErLc8toAd3f0OgOg-WjV1gonI1FrrfM"]
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

def youtube_search(options):
    try:
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
         # Merge video ids
        #video_ids = "gFa1YMEJFag,pSJ4hv28zaI,uHVEDq6RVXc,K7Om0QZy-38,DCAO6bZa31o"
        print options
        #search each video id in youtube and add it to the result
        lock = 0
        while lock == 0:
            try:
                video_response = youtube.videos().list(
                id=options,
                #contentDetails,id,liveStreamingDetails,player,recordingDetails,snippet,statistics,status,topicDetails
                part='id,snippet,statistics,status,contentDetails,topicDetails,player'
                ).execute()
                lock = 1
            except:
                try:
                    sleep(5)
                    video_response = youtube.videos().list(
                    id=options,
                    part='id,snippet,statistics,contentDetails,status,player,topicDetails'
                    ).execute()
                except:
                    print "connection error"
                    lock = 0
        with open("../data/VideoDetails/Video_"+str(options)+".json",mode="wt") as final_file:
          json.dump(video_response,final_file)
    except Exception as e:
        print options
        print e

def getDetailsForId(id,output):
    try:
        youtube_search(id)
    except Exception as e:
        print "Error Occured:",e
        output.put(id)
    return

#call as filename.py videoidsfile.txt
if __name__ == "__main__":
  pool = Pool(processes = 1)
  mgr = Manager()
  result_queue = mgr.Queue()
  f = open(argv[1],'r')
  title_list = []
  lines = f.read().splitlines()
  lines = [ids.strip() for ids in lines]
  i = 0 
  try:
      for id in lines:
        if os.path.isfile("../data/VideoDetails/Video_"+id.strip()+".json") == False:
          print id.strip()
          pool.apply_async(getDetailsForId, (id.strip(), result_queue))
      pool.close()
      pool.join()
      failed_id=[]
      while not result_queue.empty():
        failed_id += [result_queue.get()] 
      with open("../data/failed_id_getVideoDetailsFromIdFile2.txt",mode="w+") as f:
        f.write('\n'.join(failed_id))
  except HttpError, e:
    print "An HTTP error %d occurred:\n%s" % (e.resp.status, e.content)

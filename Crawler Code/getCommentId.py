import sys
from time import sleep
from sys import argv
from apiclient.discovery import build
from apiclient.errors import HttpError
from oauth2client.tools import argparser
import gzip, json
import os.path
from multiprocessing import Pool, Lock, Queue, Manager

DEVELOPER_KEY = ["AIzaSyABDLbZVLdQIiEkbHCffNnK4cXA-xDBeEQ","AIzaSyBhErLc8toAd3f0OgOg-WjV1gonI1FrrfM"]
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

# Call the API's commentThreads.list method to list the existing comment threads.
def get_comment_threads(commentIds,video_id,ordr):
  commentIds[video_id][ordr]=[]
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
  #youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,developerKey=DEVELOPER_KEY[0])
  results = youtube.commentThreads().list(
    part="snippet",
    videoId=video_id,
    textFormat="plainText",
    order=ordr,
    maxResults=100,
    fields="items/id,nextPageToken"
  ).execute()
  
  while "nextPageToken" in results:
    for item in results["items"]:
      commentIds[video_id][ordr].append(item["id"])
    results = youtube.commentThreads().list(
      part="snippet",
      videoId=video_id,
      textFormat="plainText",
      order=ordr,
      maxResults=100,
      pageToken=results["nextPageToken"],
      fields="items/id,nextPageToken"
    ).execute()
  for item in results["items"]:
    commentIds[video_id][ordr].append(item["id"])
  commentIds[video_id][ordr]=list(set(commentIds[video_id][ordr]))
  return commentIds

def new_process(id,output):
  try:
    commentIds={}
    commentIds[id]={}
    vid_dict=get_comment_threads(commentIds,id,"time")
    vid_dict=get_comment_threads(vid_dict,id,"relevance")
    print "end",id
    fname="../data/CommentIds/Video_"+id+".json"
    with open(fname, mode="wt") as f:
      json.dump(vid_dict, f)
  except Exception,e:
    print "Exception:",e
    print id

#Call this file as python getCommentId.py <videoIdFile>
if __name__ == "__main__":
  f = open(argv[1],'r')
  lines = f.read().splitlines()
  lines = [ids.strip() for ids in lines]
  pool = Pool(processes = 1)
  mgr = Manager()
  result_queue = mgr.Queue()
  for id in lines:
    fname="../data/CommentIds/Video_"+id+".json"
    if os.path.isfile(fname) == False:
      print id
      pool.apply_async(new_process, (id, result_queue))
  pool.close()
  pool.join()
  failed_id=[]
  while not result_queue.empty():
    failed_id += [result_queue.get()] 
  with open("../data/failed_id_getcommentid.txt",mode="w+") as f:
    f.write('\n'.join(failed_id))

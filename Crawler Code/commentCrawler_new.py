import sys
from time import sleep
from sys import argv
from apiclient.discovery import build
from apiclient.errors import HttpError
from oauth2client.tools import argparser
import json
import os.path
from multiprocessing import Pool, Lock, Queue, Manager

DEVELOPER_KEY = ["AIzaSyABDLbZVLdQIiEkbHCffNnK4cXA-xDBeEQ","AIzaSyBhErLc8toAd3f0OgOg-WjV1gonI1FrrfM"]
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

# Call the API's commentThreads.list method to list the existing comment threads.
# The method returns the main comment & its associated context corresponding to comment_id
def get_comment_threads(comment_id):
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
  results = youtube.commentThreads().list(
    part="snippet",
    id=comment_id,
    textFormat="plainText",
    fields="items(snippet(topLevelComment(snippet),totalReplyCount,isPublic))"
  ).execute()
  return results["items"][0]["snippet"]

# Call the API's comments.list method to list the existing comment replies.
# The method returns the list of replies to the comment with comment_id=parent_id
def get_comments(parent_id):
  commentReplyList=[]
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
  results = youtube.comments().list(
    part="snippet",
    parentId=parent_id,
    textFormat="plainText",
    fields="items(snippet),nextPageToken"
  ).execute()
  while "nextPageToken" in results:
    commentReplyList.append(results["items"])
    results = youtube.comments().list(
      part="snippet",
      parentId=parent_id,
      textFormat="plainText",
      pageToken=results["nextPageToken"],
      fields="items(snippet),nextPageToken"
    ).execute()
  commentReplyList.append(results["items"])
  return commentReplyList[0]

# Provide with list of video ids.
def new_process(id,output):
  try:
    print "starting for videoId",id
    commentIds={}
    fname="../data/CommentIds/Video_"+id+".json"
    with open(fname) as json_data:
      d=json.load(json_data)
      json_data.close()
      commentIds[id]={}
      for comment_id in d[id]["time"]:
        if comment_id not in commentIds[id]:
          commentIds[id][comment_id]={}
          vid_id=id
          try:
            commentIds[vid_id][comment_id]["main_comment"]=get_comment_threads(comment_id)
          except:
            commentIds[vid_id][comment_id]["main_comment"]=""
          try:
            commentIds[vid_id][comment_id]["replied_comment"]=get_comments(comment_id)
          except:
            commentIds[vid_id][comment_id]["replied_comment"]=""
      print "Got time relevance"
      for comment_id in d[id]["relevance"]:
        if comment_id not in commentIds[id]:
          commentIds[id][comment_id]={}
          vid_id=id
          try:
            commentIds[vid_id][comment_id]["main_comment"]=get_comment_threads(comment_id)
          except:
            commentIds[vid_id][comment_id]["main_comment"]=""
          try:
            commentIds[vid_id][comment_id]["replied_comment"]=get_comments(comment_id)
          except:
            commentIds[vid_id][comment_id]["replied_comment"]=""
      with open("../data/CommentsandReplies/Video_"+id+".json",mode="wt") as final_file:
        json.dump(commentIds,final_file)
      print "Done with VideoID:",id
  except Exception, e:
   print "exception",e
   print id
   output.put(id)

if __name__ == "__main__":
  f = open(argv[1],'r')
  lines = f.read().splitlines()
  pool = Pool(processes = 10)
  mgr = Manager()
  result_queue = mgr.Queue()
  count = 0
  for id in lines:
    if os.path.isfile("../data/CommentsandReplies/Video_"+id+".json") == False:
      count += 1
      print id,count
      pool.apply_async(new_process, (id, result_queue))  
  pool.close()
  pool.join()
  failed_id=[]
  while not result_queue.empty():
    failed_id += [result_queue.get()] 
  with open("../data/failed_id_commentcrawler_new.txt",mode="w+") as f:
    f.write('\n'.join(failed_id))
        # for vid_id in d:
        #   commentIds[vid_id]={}
        #   for ordrs in d[vid_id]:
        #     for comment_id in d[vid_id][ordrs]:
        #       if comment_id in commentIds[vid_id]:
        #         continue
        #       commentIds[vid_id][comment_id]={}
        #       try:
        #         commentIds[vid_id][comment_id]["main_comment"]=get_comment_threads(comment_id)
        #       except:
        #         commentIds[vid_id][comment_id]["main_comment"]=""
        #       try:
        #         commentIds[vid_id][comment_id]["replied_comment"]=get_comments(comment_id)
        #       except:
        #         commentIds[vid_id][comment_id]["replied_comment"]=""

import os.path
import gdata.youtube
import gdata.youtube.service
import sys
import ast
from datetime import datetime
import time
import re

def since_epoch(date_string):
   return int(time.mktime(datetime.strptime(date_string, "%Y-%m-%dT%H:%M:%S.%fZ").timetuple()) * 1000)



def comments_generator(client, video_id):
   x = 1
   count = 0
   while x==1:
            try:
               comment_feed = client.GetYouTubeVideoCommentFeed(video_id=video_id)
               while comment_feed is not None:
                 for comment in comment_feed.entry:
                   yield comment
                 next_link = comment_feed.GetNextLink()
                 if next_link is None:
                   comment_feed = None
                 else:
                     a=1
                     cnt = 0
                     while(a==1):
                         try:
                             comment_feed = client.GetYouTubeVideoCommentFeed(next_link.href)
                             a=0
                         except Exception,e:
                             print e
                             d  = str(e)
                             if(d.find("reason': 'Internal Server Error")!=-1):
                                cnt=cnt+1
                                time.sleep(5)
                             time.sleep(1)
                             print "Connectionerror"
                             if(cnt>10):
                                with open("video_comments/errorVideos.txt", "a") as myfile:
                                    myfile.write(video_id)
                                    myfile.write("\n")
                                return
                             a= 1
               x=0
               count=0
            except Exception,e:
                d = str(e)

                print d
                if(d.find("reason': 'Forbidden")!=-1):
                    if(d.find("yt:quota")==-1):
                        print "Report it for "+video_id
                        with open("video_comments/"+video_id, "a") as myfile:
                            myfile.write("Comments Forbidden in this video")
                            myfile.write("\n")
                        with open("video_comments/errorVideos.txt","a") as myfile:
                            myfile.write(video_id)
                            myfile.write(" ::Comments Fobidden")
                            myfile.write("\n")
                        return
                count=count+1
                name = type(e).__name__
                print name
                print "Connection error major"
                time.sleep(1)
                if(count>5):
                    with open("video_comments/"+video_id, "a") as myfile:
                            myfile.write("Comments Forbidden in this video")
                            myfile.write("\n")
                    with open("video_comments/errorVideos.txt", "a") as myfile:
                        myfile.write(video_id)
                        myfile.write("\n")
                    return
                x=1



def search_and_store_comments(client, keyword, video_id):
     print video_id
     if(not(os.path.isfile("video_comments/"+video_id))):
           for comment in comments_generator(client, video_id):
             author_name = comment.author[0].name.text.strip()
             text = comment.content.text
             if(text!=None):
                 text = text.strip()
             update_time = comment.updated.text.strip()
             update_time = since_epoch(update_time)

             with open("video_comments/"+video_id, "a") as myfile:
                    myfile.write(video_id+"***||***"+str(author_name)+"***||***"+str(text)+"***||***"+str(update_time))
                    myfile.write("\n")
             print (keyword, video_id, author_name, text, update_time)
     else:
         print "File exists"


def search_yt(keyword):
   client = gdata.youtube.service.YouTubeService()

   vid_pat = re.compile(r'videos/(.*?)/comments')
   vid_list = []

   for start_index in range(1, 1000, 50):
     query = gdata.youtube.service.YouTubeVideoQuery()
     query.vq = keyword
     query.max_results = 50
     query.start_index = start_index
     query.orderby = 'relevance'
     print start_index
     feed = client.YouTubeQuery(query)

     if len(feed.entry) == 0:
       break

     for entry in feed.entry:
       if entry.comments is None:
         continue
       comment_url = entry.comments.feed_link[0].href
       result = re.findall(vid_pat, comment_url)
       if len(result) > 0:
         video_id = result[0]
       else:
         continue
       if video_id not in vid_list:
         vid_list.append(video_id)
       print video_id

     time.sleep(1)

   vid_list = list(set(vid_list))
   for vid in vid_list:
     print "Executing here"
     search_and_store_comments(client, keyword, vid)
     time.sleep(3)



if __name__ == "__main__" :
   f = open('correctId.txt','r')
   title_list = []
   lines = f.read().splitlines()
   #search_yt('PoHLqb99U8Y')
   client = gdata.youtube.service.YouTubeService()

   vid_pat = re.compile(r'videos/(.*?)/comments')
   for item in lines:
     keyword = item
     # print "Searching for keyword:", keyword
     # search_yt(keyword)
     # time.sleep(1)
     search_and_store_comments(client, keyword,keyword)







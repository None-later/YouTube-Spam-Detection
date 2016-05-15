#!/usr/bin/python
import sys
import MySQLdb as mdb
from time import sleep
import time
from sys import argv
from apiclient.discovery import build
from apiclient.errors import HttpError
from oauth2client.tools import argparser

con = mdb.connect('localhost', 'sudhanshu', 'sudhanshuutube', 'utube')
cur = con.cursor()


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
        ## Use the following function only when you want to get a list of video ids based on some search query
        search_videos = []

         # Merge video ids
        #video_ids = "gFa1YMEJFag,pSJ4hv28zaI,uHVEDq6RVXc,K7Om0QZy-38,DCAO6bZa31o"
        print options
        #search each video id in youtube and add it to the result
        lock = 0
        while lock==0:
            try:
                video_response = youtube.videos().list(
                id=options,
                #contentDetails,id,liveStreamingDetails,player,recordingDetails,snippet,statistics,status,topicDetails
                part='id,snippet,statistics,status,contentDetails,topicDetails,player'
                ).execute()
                lock = 1
            except:
                try:
                    sleep(2)
                    video_response = youtube.videos().list(
                    id=options,
                    part='id,snippet,statistics,contentDetails,status,player,topicDetails'
                    ).execute()
                except:
                    print "connection error"
                    lock = 0
        videos = []
        for video_result in video_response.get("items", []):
            #print video_result
            if(video_result["snippet"]["title"]!=""):
                updateVideo(video_result) #we will use this function to update the database
            videos.append("%s, (%s)" % (video_result["snippet"]["title"],
                                  video_result["statistics"]["viewCount"]))
        if len(videos)==0:
            print "This %s does not exist" %(options)
            sql = "INSERT INTO youtube_discarded values('"+options+"')"
            try:
                cur.execute(sql)
            except:
                sql = ""
            con.commit()
        time.sleep(1)
    except:
        print "youtube_search: ",options


def updateVideo(res):

    # use initial reference table here
    try:
        video_id = res["id"]
        etag = res["etag"]


        title = res["snippet"]["title"]
        title = title.replace("\'","\\'")
        description = res["snippet"]["description"]
        description = description.replace('\'',"\\'")


        publishedAt = res["snippet"]["publishedAt"]
        publishedAt = publishedAt.replace("T"," ")
        publishedAt = publishedAt.replace(".000Z","")

        channelId = res["snippet"]["channelId"]
        channelTitle = res["snippet"]["channelTitle"]
        channelTitle = channelTitle.replace("\'","\\'")

        tags=""
        try:
            tags = ",".join(res["snippet"]["tags"])
            tags = tags.replace("\'","\\'")
        except:
            tags=""

        thumbD = ""
        thumbM = ""
        thumbH = ""
        thumbS = ""
        thumbMax = ""
        if ("thumbnails") in res["snippet"]:
            if ("default") in res["snippet"]["thumbnails"]:
                thumbD = res["snippet"]["thumbnails"]["default"]["url"]
            else:
                thumbD = "NoUrl"

            if ("medium") in res["snippet"]["thumbnails"]:
                thumbM = res["snippet"]["thumbnails"]["medium"]["url"]
            else:
                thumbM = "NoUrl"

            if ("high") in res["snippet"]["thumbnails"]:
                thumbH = res["snippet"]["thumbnails"]["high"]["url"]
            else:
                thumbH = "NoUrl"

            if ("standard") in res["snippet"]["thumbnails"]:
                thumbS = res["snippet"]["thumbnails"]["standard"]["url"]
            else:
                thumbS = "NoUrl"

            if ("maxres") in res["snippet"]["thumbnails"]:
                thumbMax = res["snippet"]["thumbnails"]["maxres"]["url"]
            else:
                thumbMax = "NoUrl"

        categoryId = res["snippet"]["categoryId"]
        liveBroadCast = ""
        if ("liveBroadcastContent") in res["snippet"]:
            liveBroadCast = res["snippet"]["liveBroadcastContent"]
        else:
            liveBroadCast = "NoData"


        sql = "INSERT INTO youtube_title VALUES('"+video_id+"','"+title+"')"
        try:
            cur.execute(sql)
            x = 4
        except:
            print "Bad title for the video"
            sql = "INSERT INTO youtube_brokentitle VALUES('"+video_id+"')"
            cur.execute(sql)

        sql = "INSERT INTO youtube_description VALUES('"+video_id+"','"+description+"')"
        try:
            cur.execute(sql)
            x = 4
        except:
            print "Bad description for the video"
            sql = "INSERT INTO youtube_brokendescription VALUES('"+video_id+"')"
            cur.execute(sql)

        # Use first table insertion here
        try:
            try:
                sql = "INSERT INTO youtube_snippet VALUES('"+video_id+"','"+publishedAt+"','"+thumbD+"','"+thumbM+"','"+thumbH+"','"+thumbS+"','"+thumbMax+"','"+channelId+"','"+channelTitle+"','"+liveBroadCast+"','"+tags+"')"
                print sql
                cur.execute(sql)
            except:
                print "duplicate"
        except UnicodeEncodeError,e:
            print "Encoding error for channel title"
            sql = "INSERT INTO youtube_snippet VALUES('"+video_id+"','"+publishedAt+"','"+thumbD+"','"+thumbM+"','"+thumbH+"','"+thumbS+"','"+thumbMax+"','"+channelId+"','Non-english-Title','"+categoryId+"','"+liveBroadCast+"','"+tags+"')"
            cur.execute(sql)

        # print res["contentDetails"]
        duration = res["contentDetails"]["duration"]
        dimension = res["contentDetails"]["dimension"]
        definition = res["contentDetails"]["definition"]
        caption = res["contentDetails"]["caption"]
        licensed=res["contentDetails"]["licensedContent"]
        print duration
        #convert duration to seconds
        y = 0
        m = 0
        if(duration.find("PT")!=-1):
            x = duration.split("PT")
            duration = x[1]
        elif(duration.find("P")!=-1):
            x = duration.split("P")
            duration = x[1]
            if(duration.find("W")!=-1):
                x = duration.split("W")
                m = int(x[0])
                y = y + m*604800
                duration = x[1]
            if(duration.find("D")!=-1):
                x = duration.split("D")
                m =int(x[0])
                y = y + m*86400
                x = duration.split("T")
                duration = x[1]
        duration = x[1]
        print duration
        if duration.find("H")!=-1:
            x = duration.split("H")
            y = y+ int(x[0])*3600
            duration = x[1]
            if duration.find("M")!=-1:
                x = duration.split("M")
                y = y + int(x[0])*60
                duration = x[1]
                if duration.find("S")!=-1:
                    x = duration.split("S")
                    y = y + int(x[0])

        elif duration.find("M")!=-1:
            x = duration.split("M")
            m = int(x[0])
            y =y+m*60
            duration = x[1]
            if duration.find("S")!=-1:
                x = duration.split("S")
                y = y + int(x[0])
        else:
            x = duration.split("S")
            y = y + int(x[0])
            duration = y

        # use second table insertion here
        sql = "INSERT INTO youtube_contentDetails values('"+video_id+"',"+str(y)+",'"+dimension+"','"+definition+"','"+str(caption)+"','"+str(licensed)+"')"
        print sql
        cur.execute(sql)

        privacy = res["status"]["privacyStatus"]
        licence = ""
        try:
            license = res["status"]["license"]
        except:
            license = ""
        embeddable = res["status"]["embeddable"]
        publicStats = ""
        try:
            publicStats = res["status"]["publicStatsViewable"]
        except:
            publicStats = ""


        #use third table insertion here
        sql = "INSERT INTO youtube_status values('"+video_id+"','"+privacy+"','"+license+"','"+str(embeddable)+"','"+str(publicStats)+"')"
        print sql
        cur.execute(sql)


        viewCount = res["statistics"]["viewCount"]
        likeCount = res["statistics"]["likeCount"]
        dislikeCount = res["statistics"]["dislikeCount"]
        favoriteCount = res["statistics"]["favoriteCount"]
        commentCount = res["statistics"]["commentCount"]

        # use fourth table insertion here
        sql = "INSERT INTO youtube_statistics VALUES('"+video_id+"',"+viewCount+","+likeCount+","+dislikeCount+","+favoriteCount+","+commentCount+")"
        print sql
        cur.execute(sql)

        sql = "INSERT INTO youtube_content VALUES('"+video_id+"','"+etag+"')"
        print sql
        cur.execute(sql)



        if("topicDetails" in res):
            if("topicIds"in(res["topicDetails"])):
                for topic in res["topicDetails"]["topicIds"]:
                    sql = "INSERT INTO youtube_topicDetails VALUES('"+video_id+"','"+topic+"')"
                    print sql
                    cur.execute(sql)
                #print res["topicDetails"]["topicIds"]
            else:
                print "No topicIds"

            if("relevantTopicIds" in (res["topicDetails"])):
                for topic in res["topicDetails"]["relevantTopicIds"]:
                    sql = "INSERT INTO youtube_relevantTopic VALUES('"+video_id+"','"+topic+"')"
                    print sql
                    cur.execute(sql)

                #print res["topicDetails"]["relevantTopicIds"]
            else:
                print "No relevant topicIds"
        else: print "No topic details"
        #print res["topicDetails"]["relevantTopicIds"]
        
        if "player" in res:
            print "Player Present"
            width = (res["player"]["embedHtml"][15:18])
            height = (res["player"]["embedHtml"][28:31])
            sql = "INSERT INTO youtube_player VALUES('"+video_id+"',"+width+","+height+")"
            print sql
            try:
                cur.execute(sql)
            except:
                print "insertPlayererr: ",video_id
        con.commit()
    except:
        print "updateVideo: ",res["id"]
    #insert completion of all the entries here



def createTable():
    sql = "CREATE TABLE IF NOT EXISTS youtube_content(id varchar(13),etag varchar(60),CONSTRAINT PRIMARY KEY(id))"
    cur.execute(sql)

    sql = "CREATE TABLE IF NOT EXISTS youtube_title(id varchar(13),title VARCHAR(110),CONSTRAINT primary key(id))"
    cur.execute(sql)

    sql = "CREATE TABLE IF NOT EXISTS youtube_description(id varchar(13),description VARCHAR(5000),CONSTRAINT primary key(id))"
    cur.execute(sql)

    sql = "CREATE TABLE IF NOT EXISTS youtube_topicDetails(id varchar(13),topicAssociated varchar(20),constraint primary key(id,topicAssociated))"
    cur.execute(sql)

    sql = "CREATE TABLE IF NOT EXISTS youtube_relevantTopic(id varchar(13),relevantTopic varchar(20),constraint primary key(id,relevantTopic))"
    cur.execute(sql)

    sql = "CREATE TABLE IF NOT EXISTS youtube_brokentitle(id varchar(13))"
    cur.execute(sql)

    sql = "CREATE TABLE IF NOT EXISTS youtube_brokendescription(id varchar(13))"
    cur.execute(sql)

    sql = "CREATE TABLE IF NOT EXISTS youtube_snippet(id varchar(13),publishedAt DATETIME,thumbnails_default varchar(200),thumbnails_medium varchar(200),thumbnails_high varchar(200),thumbnails_standard varchar(200),thumbnails_maxres varchar(200),channelId VARCHAR(35),channelTitle varchar(100),liveBroadcastContent varchar(10), tags varchar(5000), CONSTRAINT PRIMARY KEY(id))"
    cur.execute(sql)

    sql = "CREATE TABLE IF NOT EXISTS youtube_contentDetails(id varchar(13),duration INTEGER,dimension varchar(4),definition varchar(4),caption varchar(6),licensedContent varchar(6),CONSTRAINT PRIMARY KEY(id))"
    cur.execute(sql)

    sql = "CREATE TABLE IF NOT EXISTS youtube_status(id varchar(13),privacy varchar(15),license varchar(20),embeddable varchar(6),publicStatsViewable varchar(6),CONSTRAINT PRIMARY KEY(id))"
    cur.execute(sql)

    sql = "CREATE TABLE IF NOT EXISTS youtube_statistics(id varchar(13),viewCount INTEGER,likeCount INTEGER,dislikeCount INTEGER,favoriteCount INTEGER,commentCount INTEGER,CONSTRAINT PRIMARY KEY(id))"
    cur.execute(sql)

    sql = "CREATE TABLE IF NOT EXISTS youtube_discarded(id varchar(13),CONSTRAINT PRIMARY KEY(id))"
    cur.execute(sql)

    sql = "CREATE TABLE IF NOT EXISTS youtube_player(id varchar(13),width INTEGER,height INTEGER,CONSTRAINT PRIMARY KEY(id))"
    cur.execute(sql)

    con.commit()

def getDetailsForId(id,output):
    try:
        sql = "select COUNT(*) FROM youtube_content WHERE id ='"+id+"'"
        print sql
        cur.execute(sql)
        if cur.fetchone()[0]==0:
            sql = "select COUNT(*) FROM youtube_discarded WHERE id ='"+id+"'"
            print sql
            cur.execute(sql)
            if cur.fetchone()[0]==0:
                print "new id"
                youtube_search(id)
    except:
        output.put(id)
    return

if __name__ == "__main__":
  f = open(argv[1],'r')
  title_list = []
  lines = f.read().splitlines()
  createTable()
  i = 0
  pool = Pool(processes = 50)
  mgr = Manager()
  result_queue = mgr.Queue()
  try:
      for id in lines:
          pool.apply_async(getDetailsForId, (id, result_queue))
      pool.close()
      pool.join()
      failed_id=[]
      while not result_queue.empty():
        failed_id += [result_queue.get()] 
      with open("../data/failed_id_getVideoDetailsFromIdFile.txt",mode="w+") as f:
        f.write('\n'.join(failed_id))
  except HttpError, e:
    print "An HTTP error %d occurred:\n%s" % (e.resp.status, e.content)
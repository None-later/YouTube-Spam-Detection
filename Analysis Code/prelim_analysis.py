# Do some analysis on the dataset:
# #Videos -> 105456
# Average #comments/video : we have access -> 74.122, in general ->169
# How much time it takes to get 300 comments and its correlation with dislikes and views -->
# Content Analysis:
# average words
# how formal the comments are -->
# If the user is abusive
# then who is he abusing -> video or uploader. To whom it has been directed. -->
# dislike/like ratio of the comment -> data not provided by API
# how many comments refer to some other video
# ratio of #(comments referring to fakes) to #(other comments)
# How many comments have similarity to metadata

import json,os,sys,time
import MySQLdb as mdb
from multiprocessing import Pool, Lock, Queue, Manager
from time import sleep
from sys import argv
import datetime as dt
import subprocess
# from nltk.corpus import stopwords
# from nltk import word_tokenize
# from nltk.stem.wordnet import WordNetLemmatizer

# stop = stopwords.words('english')
# lemma=WordNetLemmatizer()

folder_commentid_list="../data/CommentIds/"
folder_comments="../data/CommentsandReplies/"
file_oov="../data/oov.txt"
init_file="./preliminary_analysis.json"

con = mdb.connect('localhost', 'sudhanshu', 'sudhanshuutube', 'utube')
cur = con.cursor()

videoDetails=dict()

def preprocessDB(sql):
    try:
        #print sql
        cur.execute(sql)
    except:
        print "exception:",sql
    con.commit()
    return

def getDetailsFromMySQL():
    global videoDetails
    sql = "SELECT * FROM v1;"
    #print sql
    cur.execute(sql)
    for result in cur.fetchall():
        videoDetails[result[0]]=dict()
        videoDetails[result[0]]['publishedAt']=result[1].strftime('%Y-%m-%dT%H:%M:%SZ')
        videoDetails[result[0]]['viewCount']=result[2]
        videoDetails[result[0]]['likeCount']=result[3]
        videoDetails[result[0]]['dislikeCount']=result[4]
        videoDetails[result[0]]['tags']=result[5]
        videoDetails[result[0]]['commentCount']=result[6]
    return

def main():
    global videoDetails
    if os.path.isfile(init_file)==False:
        preprocessDB("DROP VIEW important_analytics;")
        preprocessDB("CREATE VIEW important_analytics as select id,publishedAt,title,viewCount,duration,definition,licensedContent,dislikeCount,likeCount,dislikeCount/likeCount as dislike_like_ratio,tags,description from youtube_snippet natural join youtube_statistics natural join youtube_contentDetails natural join youtube_description natural join youtube_title;")
        preprocessDB("CREATE VIEW v1 as select id,publishedAt,viewCount,likeCount,dislikeCount,tags,commentCount from youtube_snippet natural join youtube_statistics;")
        getDetailsFromMySQL()
        videoIds=(subprocess.Popen(["ls",folder_comments],stdout=subprocess.PIPE).communicate()[0]).split(".json\nVideo_")
        videoIds[0]=videoIds[0].strip("Video_")
        videoIds[-1]=videoIds[-1].strip(".json")
        #Video Ids for which we have comments as well as MySQL data
        for id in videoDetails.keys():
            if id not in videoIds:
                videoDetails.pop(id,None)
        with open(init_file, mode="wt") as f:
            json.dump(videoDetails,f)
    else:
        with open(init_file) as f:
            videoDetails=json.load(f)
    for id in videoDetails.keys():
        pubdate=dt.datetime.strptime(videoDetails[id]['publishedAt'],"%Y-%m-%dT%H:%M:%SZ")
        if 'CommentRatePerDay' not in videoDetails[id]:
            with open(folder_comments+"Video_"+id+".json") as f:
                commentDetails=json.load(f)[id]
            videoDetails[id]['CommentRatePerDay'] =[0]*366
            for cmntid in commentDetails:
                try:
                    cmntdate=(commentDetails[cmntid]['main_comment']['topLevelComment']['snippet']['publishedAt'])[0:19]
                    cmntdate=dt.datetime.strptime(cmntdate,"%Y-%m-%dT%H:%M:%S")
                    print cmntdate
                    print pubdate
                    diffdays=abs(int((cmntdate-pubdate).days))
                    if diffdays <= 365 :
                        videoDetails[id]['CommentRatePerDay'][diffdays] +=1
                    print id,cmntdate,pubdate,diffdays,cmntid
                    for repcmnt in commentDetails[cmntid]['replied_comment']:
                        cmntdate=(repcmnt['snippet']['publishedAt'])[0:19]
                        cmntdate=dt.datetime.strptime(cmntdate,"%Y-%m-%dT%H:%M:%S")
                        diffdays=abs(int((cmntdate-pubdate).days))
                        if diffdays <= 365 :
                            videoDetails[id]['CommentRatePerDay'][diffdays] +=1
                except:
                    print commentDetails[cmntid]
    with open(init_file, mode="wt") as f:
            json.dump(videoDetails,f)
if __name__ == '__main__':
    main()
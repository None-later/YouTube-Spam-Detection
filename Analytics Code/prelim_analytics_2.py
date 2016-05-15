#Formalness and towards whom is the comment directed. Video or the uploader
import json,os,sys,time
from multiprocessing import Pool, Lock, Queue, Manager
from time import sleep
from sys import argv
import datetime as dt
import subprocess
from nltk.corpus import stopwords
from nltk import word_tokenize
from nltk.stem.wordnet import WordNetLemmatizer
import formal
import re

stop = stopwords.words('english')
lemma=WordNetLemmatizer()

folder_comments="../data/CommentsandReplies/"
folder_modified_comments="../data/CommentsandRepliesFormal/"
file_oov="../data/oov.txt"
init_file="./preliminary_analysis.json"

for i in os.listdir(folder_comments):
    #print i
    if i == ".DS_Store":
        continue
    print i
    comment_file=folder_comments+i
    commentsandreplies={}
    if os.path.isfile(folder_modified_comments+i) == True:
        continue
    with open(comment_file) as f:
        commentsandreplies=json.load(f)
    for videoid in commentsandreplies:
        for commentid in commentsandreplies[videoid]:
            try:
                comment_written=(commentsandreplies[videoid][commentid]['main_comment']['topLevelComment']['snippet']['textDisplay'].strip().encode("utf-8"))
                commentsandreplies[videoid][commentid]['main_comment']['topLevelComment']['snippet']["formal_score"]=formal.call(comment_written)
                if re.match('.*\+[a-zA-z0-9]+.*',comment_written):
                    commentsandreplies[videoid][commentid]['main_comment']['topLevelComment']['snippet']["isDirected"]=1
                else:
                    commentsandreplies[videoid][commentid]['main_comment']['topLevelComment']['snippet']["isDirected"]=0

            except Exception, e:
                print "exception: ",e,"videoid: ",videoid,"commentid: ",commentid
            for replies in commentsandreplies[videoid][commentid]['replied_comment']:
                try:
                    comment_written=replies['snippet']['textDisplay'].strip().encode("utf-8")
                    comment_written=re.sub(r'[^\w]',' ',comment_written)
                    replies['snippet']['formal_score']=formal.call(comment_written)
                    if re.match('.*\+[a-zA-z0-9]+.*',comment_written):
                        comment_written=replies['snippet']["isDirected"]=1
                    else:
                        comment_written=replies['snippet']["isDirected"]=0
                except Exception, e:
                    print "exception in reply: ",e,"videoid: ",videoid,"commentid: ",commentid
    with open(folder_modified_comments+i,mode ="wt") as f:
        json.dump(commentsandreplies,f)
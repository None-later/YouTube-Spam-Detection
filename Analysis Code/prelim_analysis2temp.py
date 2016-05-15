import json,os,sys,time
from multiprocessing import Pool, Lock, Queue, Manager
from time import sleep
from sys import argv
import datetime as dt
import subprocess
from nltk.corpus import stopwords
from nltk import word_tokenize
from nltk.stem.wordnet import WordNetLemmatizer
import formal,sentiment,inappropriate
import re

folder_comments = "../data/CommentsandReplies/"
folder_modified_comments = "../data/CommentsandRepliesShortlisted/"
file_oov="./BOW Files/oov.txt"

#sentiment,formalness,inappropriateness
def setFeatures(comment_file):
	print "comment_file :",comment_file
	commentsandreplies={}
	with open(comment_file) as f:
		commentsandreplies=json.load(f)
	for videoid in commentsandreplies:
		print "Number of Comments:",len(commentsandreplies[videoid])
		currComment = 0
		for commentid in commentsandreplies[videoid]:
			currComment += 1
			if currComment % 20 == 0:
				print currComment
			try:
				comment_written=(commentsandreplies[videoid][commentid]['main_comment']['topLevelComment']['snippet']['textDisplay'].strip().encode("utf-8"))
				commentsandreplies[videoid][commentid]['main_comment']['topLevelComment']['snippet']["formal_score"]=formal.call(comment_written)
				commentsandreplies[videoid][commentid]['main_comment']['topLevelComment']['snippet']["inappropriate_score"]=inappropriate.call(comment_written)
				commentsandreplies[videoid][commentid]['main_comment']['topLevelComment']['snippet']["sentiment_score"]=sentiment.call(comment_written)
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
					replies['snippet']['inappropriate_score']=inappropriate.call(comment_written)
					replies['snippet']['sentiment_score']=sentiment.call(comment_written)
					if re.match('.*\+[a-zA-z0-9]+.*',comment_written):
						comment_written=replies['snippet']["isDirected"]=1
					else:
						comment_written=replies['snippet']["isDirected"]=0
				except Exception, e:
					print "exception in reply: ",e,"videoid: ",videoid,"commentid: ",commentid
	return commentsandreplies

	
# Call as file with the list of videoid which needs to be processed.
if __name__ == '__main__':
	inappropriate.init()
	vid_list=list()
	with open(argv[1]) as f:
		vid_list = f.readlines()
	vid_list = [files for files in vid_list]
	for videoid in vid_list:
		if os.path.isfile(folder_modified_comments + "Video_" + videoid.strip() + ".json") == True:
			continue
		print videoid.strip()
		try:
			commentsandreplies_new = setFeatures( folder_comments + "Video_" + videoid.strip() + ".json" )
			#print commentsandreplies_new
			with open( folder_modified_comments + "Video_" + videoid.strip() + ".json", mode ="wt" ) as f:
				json.dump(commentsandreplies_new,f)
		except Exception, e:
			print "exception for videoid: ",videoid
		print "Done with videoid :",videoid

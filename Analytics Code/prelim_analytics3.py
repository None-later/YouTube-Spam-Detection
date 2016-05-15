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
file_oov="./BOW\ Files/oov.txt"

#sentiment,formalness,inappropriateness
def setFeatures(comment_file):
	commentsandreplies={}
	with open(comment_file) as f:
		commentsandreplies=json.load(f)
	for videoid in commentsandreplies:
		for commentid in commentsandreplies[videoid]:
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

def new_process(videoid,output):
	try:
		commentsandreplies_new = setFeatures( folder_comments + "Video_" + videoid + ".json" )
		with open( folder_modified_comments + "Video_" + videoid + ".json", mode ="wt" ) as f:
			json.dump(commentsandreplies_new,f)
	except Exception, e:
		print "exception in Process for videoid: ",videoid
	output.put(videoid)

# Call as file with the list of videoid which needs to be processed.
if __name__ == '__main__':
	pool = Pool(processes = 5)
	mgr = Manager()
	result_queue = mgr.Queue()
	vid_list = argv[1]
	vid_list = [files.strip() for files in vid_list]
	for videoid in vid_list:
		if os.path.isfile( folder_modified_comments + "Video_" + videoid + ".json" ) == False:
			print videoid
			pool.apply_async(new_process, (videoid, result_queue))
	pool.close()
	pool.join()
	failed_id=[]
	while not result_queue.empty():
		failed_id += [result_queue.get()] 
	with open("./failed_id_prelim_analysis2.txt",mode="w+") as f:
		f.write('\n'.join(failed_id))
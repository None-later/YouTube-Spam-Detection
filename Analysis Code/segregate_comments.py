import json,os,sys,time
from multiprocessing import Pool, Lock, Queue, Manager
from time import sleep
from sys import argv
import datetime as dt
import subprocess
from math import*
from nltk.corpus import stopwords
from nltk import word_tokenize
from nltk.stem.wordnet import WordNetLemmatizer
import numpy as np
# import formal,sentiment,inappropriate
import re

folder_comments = "../data/CommentsandRepliesShortlisted/"
folder_videos = "../data/VideoDetails/"
folder_channels = "../data/ChannelDetails/"
folder_commentIds = "../data/CommentIds/"
folder_commentRelevance = "../data/CommentsandRepliesRelevance/"
folder_commentLiked = "../data/CommentsandRepliesLiked/"
folder_commentLikedRelevance = "../data/CommentsandRepliesLikedRelevance/"
folder_commentfirstNdays = "../data/CommentsandRepliesfirstNdays/"

def getVideoTime(video_file):
	with open(video_file) as f:
		videoDetails = json.load(f)
	return dt.datetime.strptime(videoDetails["items"][0]["snippet"]["publishedAt"].encode("utf-8")[0:19],'%Y-%m-%dT%H:%M:%S')

def getCommentRelevance(comment_file,relevant_commentid):
	
	with open(comment_file) as f:
		commentsandreplies = json.load(f)
	commentsandreplies_new = {}
	
	for videoid in commentsandreplies:
		commentsandreplies_new[str(videoid.encode("utf-8"))]={}
		for commentid in commentsandreplies[videoid]:
			try:
				if str(commentid.encode("utf-8")) in relevant_commentid:
					commentsandreplies_new[str(videoid.encode("utf-8"))][str(commentid.encode("utf-8"))] = commentsandreplies[str(videoid.encode("utf-8"))][str(commentid.encode("utf-8"))]
			except Exception,e:
				print commentid

	return commentsandreplies_new




def getCommentLiked(comment_file):
	with open(comment_file) as f:
		commentsandreplies=json.load(f)
	commentsandreplies_new = {}
	
	for videoid in commentsandreplies:
		commentsandreplies_new[str(videoid.encode("utf-8"))]={}
		for commentid in commentsandreplies[videoid]:
			commentsandreplies_new[str(videoid.encode("utf-8"))][str(commentid.encode("utf-8"))] = {}
			try:
				lCount = commentsandreplies[str(videoid.encode("utf-8"))][str(commentid.encode("utf-8"))]['main_comment']['topLevelComment']['snippet']['likeCount']
				if(lCount > 0):
					commentsandreplies_new[str(videoid.encode("utf-8"))][str(commentid.encode("utf-8"))]['main_comment'] = commentsandreplies[str(videoid.encode("utf-8"))][str(commentid.encode("utf-8"))]['main_comment']
			except Exception,e:
				print commentid
			commentsandreplies_new[str(videoid.encode("utf-8"))][str(commentid.encode("utf-8"))]['replied_comment'] = []
			try:
				for replies in commentsandreplies[videoid][commentid]['replied_comment']:
					lCount = replies['snippet']['likeCount']
					if(lCount > 0):
						commentsandreplies_new[str(videoid.encode("utf-8"))][str(commentid.encode("utf-8"))]['replied_comment'] += [ commentsandreplies[str(videoid.encode("utf-8"))][str(commentid.encode("utf-8"))]['replied_comment'] ]
			except Exception,e:
				print "reply:",commentid


	return commentsandreplies_new


def getCommentLikedRelevance(comment_file,relevant_commentid):
	with open(comment_file) as f:
		commentsandreplies=json.load(f)
	commentsandreplies_new = {}
	
	for videoid in commentsandreplies:
		commentsandreplies_new[str(videoid.encode("utf-8"))]={}
		for commentid in commentsandreplies[videoid]:
			commentsandreplies_new[str(videoid.encode("utf-8"))][str(commentid.encode("utf-8"))] = {}
			try:
				lCount = commentsandreplies[str(videoid.encode("utf-8"))][str(commentid.encode("utf-8"))]['main_comment']['topLevelComment']['snippet']['likeCount']
				if(lCount > 0 and str(commentid.encode("utf-8")) in relevant_commentid):
					commentsandreplies_new[str(videoid.encode("utf-8"))][str(commentid.encode("utf-8"))] = commentsandreplies[str(videoid.encode("utf-8"))][str(commentid.encode("utf-8"))]
			except Exception,e:
				print commentid
			
			commentsandreplies_new[str(videoid.encode("utf-8"))][str(commentid.encode("utf-8"))]['replied_comment'] = []
			try:
				for replies in commentsandreplies[videoid][commentid]['replied_comment']:
					lCount = replies['snippet']['likeCount']
					if(lCount > 0):
						commentsandreplies_new[str(videoid.encode("utf-8"))][str(commentid.encode("utf-8"))]['replied_comment'] += [ commentsandreplies[str(videoid.encode("utf-8"))][str(commentid.encode("utf-8"))]['replied_comment'] ]
			except Exception,e:
				print "reply:",commentid
	
	return commentsandreplies_new
	

def getCommentfirstNdays(comment_file,n,pub_date):
	with open(comment_file) as f:
		commentsandreplies=json.load(f)
	commentsandreplies_new = {}
	
	for videoid in commentsandreplies:
		commentsandreplies_new[str(videoid.encode("utf-8"))]={}
		for commentid in commentsandreplies[videoid]:
			commentsandreplies_new[str(videoid.encode("utf-8"))][str(commentid.encode("utf-8"))] = {}
			try:
				cmntdate = (commentsandreplies[str(videoid.encode("utf-8"))][str(commentid.encode("utf-8"))]['main_comment']['topLevelComment']['snippet']['publishedAt']).encode("utf-8")[0:19]
				cmntdate = dt.datetime.strptime(cmntdate,"%Y-%m-%dT%H:%M:%S")
				diffdays = abs(int((cmntdate-pub_date).days))
				if diffdays <= n :
					commentsandreplies_new[str(videoid.encode("utf-8"))][str(commentid.encode("utf-8"))] = commentsandreplies[str(videoid.encode("utf-8"))][str(commentid.encode("utf-8"))]
			except Exception,e:
				print commentid
			
			commentsandreplies_new[str(videoid.encode("utf-8"))][str(commentid.encode("utf-8"))]['replied_comment'] = []
			try:
				for replies in commentsandreplies[videoid][commentid]['replied_comment']:
					cmntdate = (replies['snippet']['publishedAt']).encode("utf-8")[0:19]
					cmntdate = dt.datetime.strptime(cmntdate,"%Y-%m-%dT%H:%M:%S")
					diffdays = abs(int((cmntdate-pubdate).days))
					if diffdays <= n :
						commentsandreplies_new[str(videoid.encode("utf-8"))][str(commentid.encode("utf-8"))]['replied_comment'] += [ commentsandreplies[str(videoid.encode("utf-8"))][str(commentid.encode("utf-8"))]['replied_comment'] ]
			except Exception,e:
				print "reply:",commentid

	return commentsandreplies_new

def gatherData(videoid, relevant_commentid, pub_date,no_days):
	global folder_commentfirstNdays
	global folder_commentLiked
	global folder_commentRelevance
	global folder_commentLikedRelevance

	comment_file = folder_comments + "Video_" + videoid.strip() + ".json"
	if os.path.isfile(comment_file) == True:

		# curFile = folder_commentRelevance + "Video_" + videoid + ".json"
		# if os.path.isfile( curFile ) == False:
		# 	commentsandreplies_new = getCommentRelevance(comment_file, relevant_commentid)
		# 	with open( curFile, mode ="wt" ) as f:
		# 		json.dump(commentsandreplies_new,f)
		
		# curFile = folder_commentLikedRelevance + "Video_" + videoid + ".json"
		# if os.path.isfile( curFile ) == False:
		# 	commentsandreplies_new = getCommentLikedRelevance(comment_file, relevant_commentid)
		# 	with open( curFile, mode ="wt" ) as f:
		# 		json.dump(commentsandreplies_new,f)

		# curFile = folder_commentLiked + "Video_" + videoid + ".json"
		# if os.path.isfile( curFile ) == False:
		# 	commentsandreplies_new = getCommentLiked(comment_file)
		# 	with open( curFile, mode ="wt" ) as f:
		# 		json.dump(commentsandreplies_new,f)

		curFile = folder_commentfirstNdays + "Video_" + videoid + ".json"
		if os.path.isfile( curFile ) == False:
			commentsandreplies_new = getCommentfirstNdays(comment_file, no_days, pub_date)
			with open( curFile, mode ="wt" ) as f:
				json.dump(commentsandreplies_new,f)

# python <filename> videoIdsList <no. of days>
if __name__ == '__main__':
	global folder_commentfirstNdays
	global folder_commentLiked
	global folder_commentRelevance
	global folder_commentLikedRelevance
	vid_list=list()
	
	with open(argv[1]) as f:
		vid_list = f.readlines()

	no_days = int(argv[2])

	vid_list = [videoid.strip() for videoid in vid_list]
	folder_commentfirstNdays = "../data/CommentsandRepliesfirst"+argv[2]+"days/"
	if not os.path.exists(folder_commentfirstNdays):
		os.makedirs(folder_commentfirstNdays)

	if not os.path.exists(folder_commentLiked):
		os.makedirs(folder_commentLiked)

	if not os.path.exists(folder_commentRelevance):
		os.makedirs(folder_commentRelevance)

	if not os.path.exists(folder_commentLikedRelevance):
		os.makedirs(folder_commentLikedRelevance)

	for videoid in vid_list:
		print "Running:",videoid
		pub_date = getVideoTime(folder_videos + "Video_" + videoid.strip() + ".json")
		try:
			with open(folder_commentIds + "Video_" + videoid.strip() + ".json") as f:
				relevant_commentid = json.load(f)[videoid.strip()]['relevance']
			relevant_commentid = [commentid.encode("utf-8") for commentid in relevant_commentid]
			gatherData(videoid, relevant_commentid, pub_date,no_days)
		except Exception,e:
			print "exception videoid:",videoid.strip(),", exception:",e

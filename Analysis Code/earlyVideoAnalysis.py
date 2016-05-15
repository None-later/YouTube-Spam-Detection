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

res = {}
count_exception = 0
May12Date = dt.datetime.strptime("2016-05-12T00:00:00", '%Y-%m-%dT%H:%M:%S')
statsCommentVsLikes = [0]*4
commentCounts = []
viewCounts = []

def getCommentCount(files):
	with open("../data/CommentsandReplies/"+files) as f:
		commentsandreplies=json.load(f)
	countComment  = 0
	for videoid in commentsandreplies:
		countComment = len(commentsandreplies[str(videoid.encode("utf-8"))])
		for commentid in commentsandreplies[str(videoid.encode("utf-8"))]:
			countComment += len(commentsandreplies[str(videoid.encode("utf-8"))][str(commentid.encode("utf-8"))]['replied_comment'])
	return countComment

def getStats(files):
	global res, count_exception,viewCounts,commentCounts
	with open("../data/VideoDetails/"+files,"r") as f:
		info = json.load(f)
	res[files] = dict()
	try:
		pubdate = dt.datetime.strptime(info["items"][0]["snippet"]["publishedAt"].encode("utf-8")[0:19],'%Y-%m-%dT%H:%M:%S')
	except:
		pubdate = dt.datetime.strptime("2016-05-01T00:00:00", '%Y-%m-%dT%H:%M:%S')
	diffdays = abs(int((May12Date-pubdate).days))
	res[files]["daysOldFromMay12"] = diffdays
	try:
		# print "here"
		res[files]["commentCount"] = getCommentCount(files)
		commentCounts += [res[files]["commentCount"]]
	except:
		res[files]["commentCount"] = 0
	# print "out of here"
	try:
		res[files]["viewCount"] = int(info['items'][0]['statistics']['viewCount'])
		viewCounts += [res[files]["viewCount"]]
	except:
		res[files]["viewCount"] = 0
	try:
		res[files]["likeCount"] = int(info['items'][0]['statistics']['likeCount'])
	except:
		res[files]["likeCount"] = 0
	try:
		res[files]["dislikeCount"] = int(info['items'][0]['statistics']['dislikeCount'])
	except:
		res[files]["dislikeCount"] = 0
	try:
		if res[files]["commentCount"] == 0 and res[files]["likeCount"] == 0:
			statsCommentVsLikes[0] += 1
		elif res[files]["commentCount"] == 0 and res[files]["likeCount"] != 0:
			statsCommentVsLikes[1] += 1
		elif res[files]["commentCount"] != 0 and res[files]["likeCount"] == 0:
			statsCommentVsLikes[2] += 1
		else:
			statsCommentVsLikes[3] += 1
	except:
		statsCommentVsLikes[3] += 0
	try:
		res[files]["dislikeLikeRatio"] = float(info['items'][0]['statistics']['dislikeCount']) / float(info['items'][0]['statistics']['likeCount'])
	except:
		res[files]["dislikeLikeRatio"] = 0

def getShortlistedVideos(commentThreshold, dislikelikeThreshold):
	cnt = 0
	for files in res:
		if res[files]["commentCount"] > commentThreshold and res[files]["dislikeLikeRatio"] > dislikelikeThreshold:
			cnt += 1
			print files
	print cnt

if __name__ == '__main__':
	global res, count_exception,viewCounts,commentCounts
	with open(argv[1]) as f:
		for fname in f:
			getStats("Video_" + fname.strip() + ".json")
	with open("../data/earlyVideoAnalysis.json",mode="wt") as final_file:
		json.dump(res,final_file)
	print "Both 0: ",statsCommentVsLikes[0]
	print "Comment 0: ",statsCommentVsLikes[1]
	print "Likes 0: ",statsCommentVsLikes[2]
	print "Both !0: ",statsCommentVsLikes[3]
	meanComments =  np.mean(np.array(commentCounts))
	stddevComments = np.std(np.array(commentCounts))
	getShortlistedVideos(meanComments + stddevComments, 0.3)

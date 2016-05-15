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
folder_comments = "../data/CommentsandRepliesLiked/"
folder_videos = "../data/VideoDetails/"
folder_channels = "../data/ChannelDetails/"
annotateFile = "../data/annotateResult_final.json"
def getVideoFeatures(video_file):
	global folder_comments
	global folder_videos
	global folder_channels
	global annotateFile
	featureVector = {}
	videoDetails = {}
	with open(video_file) as f:
		videoDetails = json.load(f)
	
	featureVector["definition"] = 0
	featureVector["licensedContent"] = 0
	featureVector["publishedAt"] = ""
	featureVector["commentCountRatio"] = 0
	featureVector["favoriteCountRatio"] = 0
	featureVector["dislikeCountRatio"] = 0
	featureVector["likeCountRatio"] = 0
	featureVector["dislikelikeRatio"] = 0
	featureVector["tags"] = set([])
	try:
		if videoDetails["items"][0]["contentDetails"]["definition"].encode("utf-8") == "hd":
			featureVector["definition"] = 1
		else:
			featureVector["definition"] = 0
		featureVector["licensedContent"] = 0
		if videoDetails["items"][0]["contentDetails"]["licensedContent"] == True:
			featureVector["licensedContent"] = 1
		featureVector["publishedAt"] = dt.datetime.strptime(videoDetails["items"][0]["snippet"]["publishedAt"].encode("utf-8")[0:19],'%Y-%m-%dT%H:%M:%S')
		totalViews = max(videoDetails["items"][0]["statistics"]["viewCount"],1)
		featureVector["commentCountRatio"] = float(videoDetails["items"][0]["statistics"]["commentCount"])  / float(totalViews)
		featureVector["favoriteCountRatio"] = float(videoDetails["items"][0]["statistics"]["favoriteCount"])  / float(totalViews)
		featureVector["dislikeCountRatio"] = float(videoDetails["items"][0]["statistics"]["dislikeCount"])  / float(totalViews)
		featureVector["likeCountRatio"] = float(videoDetails["items"][0]["statistics"]["likeCount"])  / float(totalViews)
		if featureVector["likeCountRatio"]>0:
			featureVector["dislikelikeRatio"] = float(featureVector["dislikeCountRatio"])  / float(featureVector["likeCountRatio"])
		else:
			featureVector["dislikelikeRatio"] = featureVector["dislikeCountRatio"]
		description = videoDetails["items"][0]["snippet"]["description"].encode("utf-8")
		tags = videoDetails["items"][0]["snippet"]["tags"]
		tags += word_tokenize(description)
		tag_new = list()		
		for line in tags:
			for val in line.split():
				tag_new += [val.encode("utf-8").lower().strip(" \r\n\t")]
		featureVector["tags"] = set(tag_new)
	except Exception,e:
		print "exception VideoFeatures:",e
	
	return featureVector

def getCommentFeatures(comment_file, videodesc_set,pubdate,toConsider):
	global folder_comments
	global folder_videos
	global folder_channels
	global annotateFile
	featureVector={}
	commentsandreplies={}	
	with open(comment_file) as f:
		commentsandreplies=json.load(f)

	formal_score = [0]*10
	inappropriate_score = [0]*10
	sentiment_score = [0]*20
	jaccard_score = [0]*10
	comment_temporal_pattern = [0]*366
	directed = 0
	totalComments = 0
	totallikeCounts = 0
	totalConversations = 0
	for videoid in commentsandreplies:
		for commentid in commentsandreplies[str(videoid.encode("utf-8"))]:
			try:
				comment_written=(commentsandreplies[str(videoid.encode("utf-8"))][str(commentid.encode("utf-8"))]['main_comment']['topLevelComment']['snippet']['textDisplay'].strip().encode("utf-8"))
				fscore = commentsandreplies[str(videoid.encode("utf-8"))][str(commentid.encode("utf-8"))]['main_comment']['topLevelComment']['snippet']["formal_score"]
				iscore = commentsandreplies[str(videoid.encode("utf-8"))][str(commentid.encode("utf-8"))]['main_comment']['topLevelComment']['snippet']["inappropriate_score"]
				sscore = commentsandreplies[str(videoid.encode("utf-8"))][str(commentid.encode("utf-8"))]['main_comment']['topLevelComment']['snippet']["sentiment_score"]
				sscore = 100 * (sscore + 1)
				lCount = commentsandreplies[str(videoid.encode("utf-8"))][str(commentid.encode("utf-8"))]['main_comment']['topLevelComment']['snippet']['likeCount']
				totalConversations += (len(commentsandreplies[str(videoid.encode("utf-8"))][str(commentid.encode("utf-8"))]['replied_comment']) > 0)
				cmntdate = (commentsandreplies[str(videoid.encode("utf-8"))][str(commentid.encode("utf-8"))]['main_comment']['topLevelComment']['snippet']['publishedAt']).encode("utf-8")[0:19]
				cmntdate = dt.datetime.strptime(cmntdate,"%Y-%m-%dT%H:%M:%S")
				diffdays = abs(int((cmntdate-pubdate).days))
				if diffdays <= 365 :
					comment_temporal_pattern[diffdays] += 1
				# print "fscore:",fscore,", iscore:",iscore,", sscore:",sscore,", lCount:",lCount
				formal_score[ max( int( (fscore-1)/10 ) , 0) ] += fscore
				inappropriate_score[ max( int( (iscore-1)/10 ) , 0) ] += iscore
				sentiment_score[ max( int( (sscore-1)/10 ) , 0) ] += sscore
				# print "Comment:\n",comment_written
				if re.match('.*\+[a-zA-z0-9]+.*',comment_written,re.UNICODE):
					directed += 1
					# print "directed"
				# print "After directed"
				comment_words = word_tokenize(comment_written)
				comment_words = [word.lower().strip(" \r\n\t") for word in comment_words]
				comment_set = set(comment_words)
				# print "CommentSet:",comment_set
				intersection_cardinality = len(set.intersection(*[videodesc_set, comment_set]))
				union_cardinality = len(set.union(*[videodesc_set, comment_set]))
				jaccard_val = intersection_cardinality*100/float(union_cardinality)
				jaccard_score[int(jaccard_val - 1)/10] += (0.1+lCount * toConsider)
				totalComments += 1
				totallikeCounts += lCount * toConsider
				# print "\n"
			except Exception, e:
				print "exception Comment: ",e,"videoid: ",videoid,"commentid: ",commentid
			#Seeing all the replies to the main comment
			for replies in commentsandreplies[str(videoid.encode("utf-8"))][str(commentid.encode("utf-8"))]['replied_comment']:
				try:
					comment_written=replies['snippet']['textDisplay'].strip().encode("utf-8")
					fscore = replies['snippet']['formal_score']
					iscore = replies['snippet']['inappropriate_score']
					sscore = replies['snippet']['sentiment_score']
					sscore = 100 * (sscore + 1)
					lCount = replies['snippet']['likeCount']
					cmntdate = (replies['snippet']['publishedAt']).encode("utf-8")[0:19]
					cmntdate = dt.datetime.strptime(cmntdate,"%Y-%m-%dT%H:%M:%S")
					diffdays = abs(int((cmntdate-pubdate).days))
					if diffdays <= 365 :
						comment_temporal_pattern[diffdays] += 1
					# print "fscore:",fscore,", iscore:",iscore,", sscore:",sscore,", lCount:",lCount
					formal_score[ max( int( (fscore-1)/10 ) , 0) ] += fscore
					inappropriate_score[ max( int( (iscore-1)/10 ) , 0) ] += iscore
					sentiment_score[ max( int( (sscore-1)/10 ) , 0) ] += sscore
					# print "CommentReplied:\n",comment_written
					if re.match('.*\+[a-zA-z0-9]+.*',comment_written,re.UNICODE):
						directed += 1
						# print "directed"
					comment_words = word_tokenize(comment_written)
					comment_words = [word.lower().strip(" \r\n\t") for word in comment_words]
					comment_set = set(comment_words)
					# print "CommentSet:",comment_set
					intersection_cardinality = len(set.intersection(*[videodesc_set, comment_set]))
					union_cardinality = len(set.union(*[videodesc_set, comment_set]))
					jaccard_val = intersection_cardinality*100/float(union_cardinality)
					jaccard_score[int(jaccard_val - 1)/10] += (0.1+lCount * toConsider)
					totalComments += 1
					totallikeCounts += lCount * toConsider
				except Exception, e:
					print "exception Comment in reply: ",e,"videoid: ",videoid,"commentid: ",commentid
	try:
		x=1
		comment_temporal_pattern = [val*1.0 / totalComments for val in comment_temporal_pattern]
	except Exception,e:
		print "exception Comment-zeros:",e
		formal_score = [0]*10
		inappropriate_score = [0]*10
		sentiment_score = [0]*20
		jaccard_score = [0]*10
	if totalComments <= 0:
		return -1;
	featureVector['formal_score'] = sum(formal_score) / totalComments
	featureVector['inappropriate_score'] = sum(inappropriate_score) / totalComments
	featureVector['sentiment_score'] = sum(sentiment_score) / totalComments
	featureVector['jaccard_score'] = sum(jaccard_score) / totalComments
	featureVector['comment_temporal_pattern'] = comment_temporal_pattern
	featureVector['ratioDirected'] = directed * 1.0 / max(totalComments,1)
	featureVector['ratioConversation'] = totalConversations * 1.0 / max(totalComments,1)
	return featureVector
if __name__ == '__main__':
	global folder_comments
	global folder_videos
	global folder_channels
	global annotateFile

	annotateResult ={}
	
	vid_list=list()
	
	videofVector = {}
	commentsfVector = {}
	channelfVector = {}
	commentsfVectorTemp = {}

	with open(annotateFile) as f:
		annotateResult = json.load(f)
	
	with open(argv[1]) as f:
		vid_list = f.readlines()
	
	curr = 1
	v=0
	sums=0
	f=i=s=j=rD=rC=cT1=cT2=cT3=cT4=cT7=0
	for videoid in vid_list:
		videoid = videoid.strip()
		try:
			if annotateResult[videoid] == 2 or annotateResult[videoid] == 1:
		 		continue
		except:
			continue
		if os.path.isfile(folder_videos + "Video_" + videoid.strip() + ".json") == False or os.path.isfile(folder_comments + "Video_" + videoid.strip() + ".json") == False or os.path.isfile(folder_channels + "Video_" + videoid.strip() + ".json") == False:
			continue
		print curr
		curr += 1
		sums += 1
		# print videoid
		# print folder_videos + "Video_" + videoid.strip() + ".json"
		videofVector = getVideoFeatures(folder_videos + "Video_" + videoid.strip() + ".json")
		# print videofVector
		# exit()
		commentsfVector = getCommentFeatures(folder_comments + "Video_" + videoid.strip() + ".json", videofVector["tags"],videofVector["publishedAt"],1)
		print "here"
		if commentsfVector == -1:
			continue
		else:
			v1 = commentsfVector
			f +=v1['formal_score']
			i +=v1['inappropriate_score']
			s +=v1['sentiment_score']
			j +=v1['jaccard_score']
			rD+=v1['ratioDirected']
			rC+=v1['ratioConversation']
			cT1+=v1['comment_temporal_pattern'][0]
			cT2+=v1['comment_temporal_pattern'][1]
			cT3+=v1['comment_temporal_pattern'][2]
			cT4+=v1['comment_temporal_pattern'][3]
			cT7+=v1['comment_temporal_pattern'][6]

	print (f * 1.0) / sums
	print (i * 1.0) / sums
	print (s * 1.0) / sums
	print (j * 1.0) / sums
	print (rD * 1.0) / sums
	print (rC * 1.0) / sums
	print (cT1 * 1.0) / sums
	print (cT2 * 1.0) / sums
	print (cT3 * 1.0) / sums
	print (cT4 * 1.0) / sums
	print (cT7 * 1.0) / sums
	print sums
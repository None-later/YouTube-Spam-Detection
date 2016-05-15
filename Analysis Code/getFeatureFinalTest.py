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
def getVideoFeatures(video_file):
	global folder_comments
	global folder_videos
	global folder_channels
	
	
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

def getCommentFeatures(comment_file, videodesc_set,pubdate,toConsider,bucketSize):
	global folder_comments
	global folder_videos
	global folder_channels
	
	
	featureVector={}
	commentsandreplies={}
	
	with open(comment_file) as f:
		commentsandreplies=json.load(f)
	formal_score = [0]*bucketSize
	inappropriate_score = [0]*bucketSize
	sentiment_score = [0]*bucketSize
	jaccard_score = [0]*bucketSize
	comment_temporal_pattern = [0]*541
	directed = 0
	totalComments = 0
	totallikeCounts = 0
	totalConversations = 0

	for videoid in commentsandreplies:
		for commentid in commentsandreplies[str(videoid.encode("utf-8"))]:
			try:
				comment_written=(commentsandreplies[str(videoid.encode("utf-8"))][str(commentid.encode("utf-8"))]['main_comment']['topLevelComment']['snippet']['textDisplay'].strip().encode("utf-8"))
				print "\n\n"
				#Formal Score
				try:
					fscore = commentsandreplies[str(videoid.encode("utf-8"))][str(commentid.encode("utf-8"))]['main_comment']['topLevelComment']['snippet']["formal_score"]
				except Exception,e:
					fscore = 0.0
				#Inappropriate Score
				try:
					iscore = commentsandreplies[str(videoid.encode("utf-8"))][str(commentid.encode("utf-8"))]['main_comment']['topLevelComment']['snippet']["inappropriate_score"]
				except Exception,e:
					iscore = 0.0
				#Sentiment Score
				try:
					sscore = commentsandreplies[str(videoid.encode("utf-8"))][str(commentid.encode("utf-8"))]['main_comment']['topLevelComment']['snippet']["sentiment_score"]
					sscore = 100 * (sscore + 1)
				except Exception,e:
					sscore = 0.0
				#Like Count count
				try:
					lCount = commentsandreplies[str(videoid.encode("utf-8"))][str(commentid.encode("utf-8"))]['main_comment']['topLevelComment']['snippet']['likeCount']
				except Exception,e:
					lCount = 0
				
				try:
					totalConversations += (len(commentsandreplies[str(videoid.encode("utf-8"))][str(commentid.encode("utf-8"))]['replied_comment']) > 0)
				except Exception,e:
					totalConversations = 0
				try:
					cmntdate = (commentsandreplies[str(videoid.encode("utf-8"))][str(commentid.encode("utf-8"))]['main_comment']['topLevelComment']['snippet']['publishedAt']).encode("utf-8")[0:19]
					cmntdate = dt.datetime.strptime(cmntdate,"%Y-%m-%dT%H:%M:%S")
					diffdays = abs(int((cmntdate-pubdate).days))
					if diffdays <= 540 :
						comment_temporal_pattern[diffdays] += 1
				except Exception,e:
					temp=1

				# print "fscore:",fscore,", iscore:",iscore,", sscore:",sscore,", lCount:",lCount
				print "reached here"
				print fscore,iscore,sscore
				print int( (fscore-1) * bucketSize * 1.0/100 )
				print int( (iscore-1) * bucketSize * 1.0/100 )
				print int( (sscore-1) * bucketSize * 1.0/100 )
				formal_score[ max( int( (fscore-1) * bucketSize * 1.0/100 ) , 0) ] += (0.1+lCount * toConsider)
				inappropriate_score[ max( int( (iscore-1) * bucketSize * 1.0/100 ) , 0) ] += (0.1+lCount * toConsider)
				sentiment_score[ max( int( (sscore-1) * bucketSize * 1.0/200 ) , 0) ] += (0.1+lCount * toConsider)
				print "reached here & here"
				# print "Comment:\n",comment_written
				try:
					if re.match('.*\+[a-zA-z0-9]+.*',comment_written,re.UNICODE):
						directed += 1
				except Exception,e:
					directed += 0
				
				# print "CommentSet:",comment_set
				try:
					comment_words = word_tokenize(comment_written)
					comment_words = [word.lower().strip(" \r\n\t") for word in comment_words]
					comment_set = set(comment_words)
					intersection_cardinality = len(set.intersection(*[videodesc_set, comment_set]))
					union_cardinality = len(set.union(*[videodesc_set, comment_set]))
					jaccard_val = intersection_cardinality*100/float(union_cardinality)
					jaccard_score[int((jaccard_val - 1) * bucketSize * 1.0/100)] += (0.1+lCount * toConsider)
						
				except Exception,e:
					jaccard_score[0] += (0.1+lCount * toConsider)
				
				totalComments += 1
				totallikeCounts += lCount * toConsider
			except Exception,e:
				print "exception Main Comment: ",e,"videoid: ",videoid,"commentid: ",commentid
				# print (commentsandreplies[str(videoid.encode("utf-8"))][str(commentid.encode("utf-8"))])
				# print commentsandreplies[str(videoid.encode("utf-8"))][str(commentid.encode("utf-8"))]
			

			#Seeing all the replies to the main comment
			for replies in commentsandreplies[str(videoid.encode("utf-8"))][str(commentid.encode("utf-8"))]['replied_comment']:
				try:
					comment_written=replies['snippet']['textDisplay'].strip().encode("utf-8")
					#Formal Score
					try:
						fscore = replies['snippet']['formal_score']
					except Exception, e:
						fscore = 0
					#Inappropriate Score
					try:
						iscore = replies['snippet']['inappropriate_score']
					except Exception, e:
						iscore = 0
					#Sentiment Score
					try:	
						sscore = replies['snippet']['sentiment_score']
						sscore = 100 * (sscore + 1)
					except Exception,e:
						sscore = 0
					#Like Count count
					try:
						lCount = replies['snippet']['likeCount']
					except Exception,e:
						lCount = 0

					cmntdate = (replies['snippet']['publishedAt']).encode("utf-8")[0:19]
					cmntdate = dt.datetime.strptime(cmntdate,"%Y-%m-%dT%H:%M:%S")
					diffdays = abs(int((cmntdate-pubdate).days))
					
					try:
						if diffdays <= 540 :
							comment_temporal_pattern[diffdays] += 1
					except Exception,e:
						temp = 1
						

					# print "fscore:",fscore,", iscore:",iscore,", sscore:",sscore,", lCount:",lCount
					formal_score[ max( int( (fscore-1) * bucketSize * 1.0/100 ) , 0) ] += (0.1+lCount * toConsider)
					inappropriate_score[ max( int( (iscore-1) * bucketSize * 1.0/100 ) , 0) ] += (0.1+lCount * toConsider)
					sentiment_score[ max( int( (sscore-1) * bucketSize * 1.0/200 ) , 0) ] += (0.1+lCount * toConsider)
					
					# print "CommentReplied:\n",comment_written
					try:
						if re.match('.*\+[a-zA-z0-9]+.*',comment_written,re.UNICODE):
							directed += 1
					except Exception,e:
						directed += 0
						# print "directed"
					try:
						comment_words = word_tokenize(comment_written)
						comment_words = [word.lower().strip(" \r\n\t") for word in comment_words]
						comment_set = set(comment_words)
						# print "CommentSet:",comment_set
						
						intersection_cardinality = len(set.intersection(*[videodesc_set, comment_set]))
						union_cardinality = len(set.union(*[videodesc_set, comment_set]))
						jaccard_val = intersection_cardinality*100/float(union_cardinality)

						jaccard_score[int((jaccard_val - 1) * bucketSize * 1.0/100)] += (0.1+lCount * toConsider)
					except Exception,e:
						jaccard_score[0] += (0.1+lCount * toConsider)

					totalComments += 1
					totallikeCounts += lCount * toConsider

				except Exception, e:
					print "exception Comment in reply: ",e,"videoid: ",videoid,"commentid: ",commentid
	
	#Normalising formal_score
	try:
		formal_score = formal_score * 1.0 / sum(formal_score)
	except:
		formal_score = [0]*bucketSize
	
	#Normalising inappropriate_score
	try:	
		inappropriate_score = inappropriate_score * 1.0 / sum(inappropriate_score)
	except:
		inappropriate_score = [0]*bucketSize
	
	#Normalising sentiment_score
	try:
		sentiment_score = sentiment_score * 1.0 / sum(sentiment_score)
	except:
		sentiment_score = [0]*bucketSize
	
	#Normalising jaccard_score
	try:	
		jaccard_score = jaccard_score * 1.0 / sum(jaccard_score)
	except:
		jaccard_score = [0]*bucketSize
	
	try:
		comment_temporal_pattern = [val*1.0 / totalComments for val in comment_temporal_pattern]
	except:
		comment_temporal_pattern = [0]*len(comment_temporal_pattern)
	
	if totalComments <= 0:
		return -1;

	featureVector['formal_score'] = formal_score
	featureVector['inappropriate_score'] = inappropriate_score
	featureVector['sentiment_score'] = sentiment_score
	featureVector['jaccard_score'] = jaccard_score
	featureVector['comment_temporal_pattern'] = comment_temporal_pattern
	featureVector['ratioDirected'] = directed * 1.0 / max(totalComments,1)
	featureVector['ratioConversation'] = totalConversations * 1.0 / max(totalComments,1)
	return featureVector

def getChannelFeature(channel_file):
	global folder_comments
	global folder_videos
	global folder_channels
	
	featureVector = {}
	channelDetails = {}
	
	with open(channel_file) as f:
		channelDetails = json.load(f)
	
	featureVector["commentCountRatio"] = 0
	featureVector["viewCountRatio"] = 0
	featureVector["subscriberCountRatioviews"] = 0
	featureVector["subscriberCountRatiovideo"] = 0
	# print channelDetails	
	try:
		videoCount = max(int(channelDetails["items"][0]["statistics"]["videoCount"]),1)
		featureVector["commentCountRatio"] = float(int(channelDetails["items"][0]["statistics"]["commentCount"]))  / float(videoCount)
		featureVector["viewCountRatio"] = float(int(channelDetails["items"][0]["statistics"]["viewCount"]))  / float(videoCount)
		featureVector["subscriberCountRatiovideo"] = float(int(channelDetails["items"][0]["statistics"]["subscriberCount"]))  / float(videoCount)
		featureVector["subscriberCountRatioviews"] = float(int(channelDetails["items"][0]["statistics"]["subscriberCount"]))  / float(max(int(channelDetails["items"][0]["statistics"]["viewCount"]),1))
	except Exception, e:
		print "exception in Channel:",e

	return featureVector

def gatherAllFeature(videofVector,commentsfVector,channelfVector):
	global folder_comments
	global folder_videos
	global folder_channels
	

	tempX = list()
	for el in channelfVector:
		try:
			for ele in channelfVector[el]:
				tempX += [ ele ]
		except:
			tempX += [ channelfVector[el] ]
	for el in commentsfVector:
		try:
			for ele in commentsfVector[el]:
				tempX += [ ele ]
		except:
			tempX += [ commentsfVector[el] ]

	for el in videofVector:
		if el == "tags" or el == "publishedAt":
			continue
		try:
			for ele in videofVector[el]:
				tempX += [ ele ]
		except:
			tempX += [ videofVector[el] ]

	return tempX

def getFeatureName(videofVector,commentsfVector,channelfVector):
	global folder_comments
	global folder_videos
	global folder_channels
	
	featureName = list()

	for el in channelfVector:
		try:
			cnt = 1
			for ele in channelfVector[el]:
				featureName += [ "Channel_" + str(el) + "_" + str(cnt) ]
				cnt += 1
		except:
			featureName += [ "Channel_" + str(el) ]
	for el in commentsfVector:
		try:
			cnt = 1
			for ele in commentsfVector[el]:
				featureName += [ "Comment_" + str(el) + "_" + str(cnt) ]
				cnt += 1
		except:
			featureName += [ "Comment_" + str(el) ]

	for el in videofVector:
		if el == "tags" or el == "publishedAt":
			continue
		try:
			cnt = 1
			for ele in videofVector[el]:
				featureName += [ "Video_" + str(el) + "_" + str(cnt) ]
				cnt += 1
		except:
			featureName += [ "Video_" + str(el) ]

	return featureName

#Call as python <filename> <videoIdslist> <0 - not consider lCount, 1 - consider lCount> <bucketSize>
if __name__ == '__main__':
	global folder_comments
	global folder_videos
	global folder_channels
	

	annotateResult ={}
	
	vid_list=list()
	
	videofVector = {}
	commentsfVector = {}
	commentsfVectortemp = {}
	channelfVector = {}

	X = list()
	
	with open(argv[1]) as f:
		vid_list = f.readlines()
	
	curr = 1
	for videoid in vid_list:
		if os.path.isfile(folder_videos + "Video_" + videoid.strip() + ".json") == False or os.path.isfile(folder_comments + "Video_" + videoid.strip() + ".json") == False or os.path.isfile(folder_channels + "Video_" + videoid.strip() + ".json") == False:
			continue
		print curr
		curr += 1
		# print videoid
		# print folder_videos + "Video_" + videoid.strip() + ".json"
		videofVector = getVideoFeatures(folder_videos + "Video_" + videoid.strip() + ".json")
		# print videofVector
		# exit()
		commentsfVector = getCommentFeatures(folder_comments + "Video_" + videoid.strip() + ".json", videofVector["tags"],videofVector["publishedAt"],int(argv[2]),int(argv[3]))
		if commentsfVector == -1:
			continue
		else:
			commentsfVectortemp = commentsfVector
		# print commentsfVector
		# print folder_channels + "Video_" + videoid.strip() + ".json"
		channelfVector = getChannelFeature(folder_channels + "Video_" + videoid.strip() + ".json")
		# print channelfVector
		tempX = gatherAllFeature([],commentsfVector,[])
		X += [ tempX ]
	featuresName = np.array(getFeatureName([],commentsfVectortemp,[]))
	folder_save = "./usingCommentFeature_test/"
	X = np.array(X)
	np.save(folder_save + "X-Vector",X)
	np.save(folder_save + "Features-Name",featuresName)
	print "Order of video being processed:"
	for videoid in vid_list:
		print videoid

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
import matplotlib.pyplot as plt
# import formal,sentiment,inappropriate
import re

folder_comments = "../data/CommentsandRepliesShortlisted/"
folder_videos = "../data/VideoDetails/"
folder_channels = "../data/ChannelDetails/"
annotateFile = "../data/annotateResult_final.json"
folder_plots = "../data/Plots/CommentsandRepliesShortlisted/"

FakeVideo = {}
LegitVideo = {}

def getVideoFeatures(video_file):
	
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
				
				formal_score[ max( int( (fscore-1)/10 ) , 0) ] += (1+lCount * toConsider)
				inappropriate_score[ max( int( (iscore-1)/10 ) , 0) ] += (1+lCount * toConsider)
				sentiment_score[ max( int( (sscore-1)/10 ) , 0) ] += (1+lCount * toConsider)

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

				jaccard_score[int(jaccard_val - 1)/10] += (1+lCount * toConsider)

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
					formal_score[ max( int( (fscore-1)/10 ) , 0) ] += (1+lCount * toConsider)
					inappropriate_score[ max( int( (iscore-1)/10 ) , 0) ] += (1+lCount * toConsider)
					sentiment_score[ max( int( (sscore-1)/10 ) , 0) ] += (1+lCount * toConsider)
					
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

					jaccard_score[int(jaccard_val - 1)/10] += (1+lCount * toConsider)
					
					totalComments += 1
					totallikeCounts += lCount * toConsider

				except Exception, e:
					print "exception Comment in reply: ",e,"videoid: ",videoid,"commentid: ",commentid
	try:
		formal_score = [val*1.0 / (totalComments + totallikeCounts) for val in formal_score]
		inappropriate_score = [val*1.0 / (totalComments + totallikeCounts) for val in inappropriate_score]
		sentiment_score = [val*1.0 / (totalComments + totallikeCounts) for val in sentiment_score]
		jaccard_score = [val*1.0 / (totalComments + totallikeCounts) for val in jaccard_score]
		comment_temporal_pattern = [val*1.0 / totalComments for val in comment_temporal_pattern]
	except Exception,e:
		print "exception Comment-zeros:",e
		formal_score = [0]*10
		inappropriate_score = [0]*10
		sentiment_score = [0]*20
		jaccard_score = [0]*10

	if totalComments <= 0:
		return -1;

	featureVector['formal_score'] = formal_score
	featureVector['inappropriate_score'] = inappropriate_score
	featureVector['sentiment_score'] = sentiment_score
	featureVector['jaccard_score'] = jaccard_score
	featureVector['ratioDirected'] = directed*1.0 / max(totalComments,1)
	featureVector['ratioConversation'] = totalConversations*1.0 / max(totalComments,1)
	return featureVector

def getChannelFeature(channel_file):
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

def gatherAllFeature(typeof,videofVector,commentsfVector,channelfVector):
	global FakeVideo
	global LegitVideo

	for el in channelfVector:
		if typeof == 1:
			FakeVideo["Channel_" + str(el)] = np.append(FakeVideo["Channel_" + str(el)], channelfVector[el])
		elif typeof == 0:
			LegitVideo["Channel_" + str(el)] = np.append(LegitVideo["Channel_" + str(el)], channelfVector[el])

	for el in commentsfVector:
		if "ratio" in el:
			if typeof == 1:
				FakeVideo["Comment_" + str(el)] = np.append(FakeVideo["Comment_" + str(el)], commentsfVector[el])
			elif typeof == 0:
				LegitVideo["Comment_" + str(el)] = np.append(LegitVideo["Comment_" + str(el)], commentsfVector[el])
		else:
			if typeof == 1:
				FakeVideo["Comment_" + str(el)] += np.array(commentsfVector[el])
			elif typeof == 0:
				LegitVideo["Comment_" + str(el)] += np.array(commentsfVector[el])

	for el in videofVector:
		if el == "tags" or el == "publishedAt" or el == "definition" or el == "licensedContent":
			continue
		if typeof == 1:
			FakeVideo["Video_" + str(el)] = np.append(FakeVideo["Video_" + str(el)], videofVector[el])
		elif typeof == 0:
			LegitVideo["Video_" + str(el)] = np.append(LegitVideo["Video_" + str(el)], videofVector[el])

def getFeatureName(videofVector,commentsfVector,channelfVector):
	global FakeVideo
	global LegitVideo
	FakeVideo = {}
	LegitVideo = {}

	for el in channelfVector:
		try:
			for ele in channelfVector[el]:
				FakeVideo["Channel_"+str(el)] = np.zeros(len(channelfVector[el]))
				LegitVideo["Channel_"+str(el)] = np.zeros(len(channelfVector[el]))
				break
		except:
			FakeVideo["Channel_"+str(el)] = np.empty(0)
			LegitVideo["Channel_"+str(el)] = np.empty(0)
	
	for el in commentsfVector:
		try:
			for ele in commentsfVector[el]:
				FakeVideo["Comment_"+str(el)] = np.zeros(len(commentsfVector[el]))
				LegitVideo["Comment_"+str(el)] = np.zeros(len(commentsfVector[el]))
				break
		except:
			FakeVideo[ "Comment_" + str(el) ] = np.empty(0)
			LegitVideo[ "Comment_" + str(el) ] = np.empty(0)

	for el in videofVector:
		if el == "tags" or el == "publishedAt" or el == "licensedContent" or el == "definition":
			continue
		try:
			for ele in videofVector[el]:
				FakeVideo[ "Video_" + str(el)  ] = np.zeros(len(videofVector[el]))
				LegitVideo[ "Video_" + str(el)  ] = np.zeros(len(videofVector[el]))
				break
		except:
			FakeVideo[ "Video_" + str(el) ] = np.empty(0)
			LegitVideo[ "Video_" + str(el) ] = np.empty(0)
	# print "here"
	# print FakeVideo
	# print LegitVideo

def normalizeFeature(binSize):
	global FakeVideo
	global LegitVideo
	
	fakecount = 157
	legitcount = 399
	# for el in channelfVector:
	# 	try:
	# 		binsConsider = np.histogram(np.append(FakeVideo["Channel_" + str(el)], LegitVideo["Channel_" + str(el)]),bins = binSize, normed = True)[1]
	# 		FakeVideo["Channel_" + str(el)] = np.histogram(FakeVideo["Channel_" + str(el)],bins = binsConsider,normed = True,density = False)[0]
	# 		LegitVideo["Channel_" + str(el)] = np.histogram(LegitVideo["Channel_" + str(el)],bins = binsConsider,normed = True,density = False)[0]
	# 	except Exception,e:
	# 		continue

	for el in commentsfVector:
		try:
			if "ratio" in el:
				continue
				# binsConsider = np.histogram(np.append(FakeVideo["Comment_" + str(el)], LegitVideo["Comment_" + str(el)]),bins = binSize, normed = True)[1]
				# FakeVideo["Comment_" + str(el)] = np.histogram(FakeVideo["Comment_" + str(el)],bins = binsConsider,normed = True,density = False)[0]
				# LegitVideo["Comment_" + str(el)] = np.histogram(LegitVideo["Comment_" + str(el)],bins = binsConsider,normed = True,density = False)[0]
			else:
				FakeVideo["Comment_" + str(el)] /= fakecount
				LegitVideo["Comment_" + str(el)] /= legitcount
		except Exception,e:
			continue

	# for el in videofVector:
	# 	try:
	# 		if el == "tags" or el == "publishedAt" or el == "definition" or el == "licensedContent":
	# 			continue
	# 		binsConsider = np.histogram(np.append(FakeVideo["Video_" + str(el)], LegitVideo["Video_" + str(el)]),bins = binSize, normed = True)[1]
	# 		FakeVideo["Video_" + str(el)] = np.histogram(FakeVideo["Video_" + str(el)],bins = binsConsider,normed = True,density = False)[0]
	# 		LegitVideo["Video_" + str(el)] = np.histogram(LegitVideo["Video_" + str(el)],bins = binsConsider,normed = True,density = False)[0]
	# 	except Exception,e:
	# 		continue


def plotFeatures(binSize):
	global FakeVideo
	global LegitVideo
	global folder_plots

	for el in channelfVector:
		try:
			plt.figure(1)
			binsConsider = np.histogram(np.append(FakeVideo["Channel_" + str(el)], LegitVideo["Channel_" + str(el)]),bins = binSize, normed = True)[1]
			
			fake = plt.subplot(211)
			fake.set_title("Fake " + "Channel_" + str(el))
			fake.hist(FakeVideo["Channel_" + str(el)], bins = binsConsider, facecolor = 'r')
			
			legit = plt.subplot(212)
			legit.set_title("Legit " + "Channel_" + str(el))
			legit.hist(LegitVideo["Channel_" + str(el)], bins = binsConsider, facecolor = 'g')
			
			if not os.path.exists(folder_plots):
				os.makedirs(folder_plots)
			fname = folder_plots + "Channel_" + str(el) +".png"
			plt.savefig(fname)
			plt.close()
		except Exception,e:
			continue

	for el in commentsfVector:
		try:
			plt.figure(1)
			fake = plt.subplot(211)
			fake.set_title("Fake " + "Comment_" + str(el))
			legit = plt.subplot(212)
			legit.set_title("Legit " + "Comment_" + str(el))
			if "ratio" in el:
				binsConsider = np.histogram(np.append(FakeVideo["Comment_" + str(el)], LegitVideo["Comment_" + str(el)]),bins = binSize, normed = True)[1]
				fake.hist(FakeVideo["Comment_" + str(el)], bins = binsConsider, facecolor = 'r')
				legit.hist(LegitVideo["Comment_" + str(el)], bins = binsConsider, facecolor = 'g')
			else:
				fake.plot(np.arange(len(FakeVideo["Comment_" + str(el)])) + 1, FakeVideo["Comment_" + str(el)], 'r')
				legit.plot(np.arange(len(LegitVideo["Comment_" + str(el)])) + 1, LegitVideo["Comment_" + str(el)], 'g')
			
			if not os.path.exists(folder_plots):
				os.makedirs(folder_plots)
			fname = folder_plots + "Comment_" + str(el) +".png"
			plt.savefig(fname)
			plt.close()
		except Exception,e:
			continue

	for el in videofVector:
		if el == "tags" or el == "publishedAt" or el == "definition" or el == "licensedContent":
			continue
		try:	
			plt.figure(1)
			binsConsider = np.histogram(np.append(FakeVideo["Video_" + str(el)], LegitVideo["Video_" + str(el)]),bins = binSize, normed = True)[1]
			
			fake = plt.subplot(211)
			fake.set_title("Fake " + "Video_" + str(el))
			fake.hist(FakeVideo["Video_" + str(el)], bins = binsConsider, facecolor = 'r')
			
			legit = plt.subplot(212)
			legit.set_title("Legit " + "Video_" + str(el))
			legit.hist(LegitVideo["Video_" + str(el)], bins = binsConsider, facecolor = 'g')
			
			if not os.path.exists(folder_plots):
				os.makedirs(folder_plots)
			fname = folder_plots + "Video_" + str(el) +".png"
			plt.savefig(fname)
			plt.close()
		except Exception,e:
			continue


#Call as python <filename> <videoIdslist> <binSize>
if __name__ == '__main__':
	global folder_plots
	global folder_comments
	global FakeVideo
	global LegitVideo
	folder_commentRelevance = "CommentsandRepliesRelevance/"
	folder_commentLiked = "CommentsandRepliesLiked/"
	folder_commentLikedRelevance = "CommentsandRepliesLikedRelevance/"
	folder_commentfirstNdays = "CommentsandRepliesfirst5days/"
	commentsFolderSet = ["../data/CommentsandRepliesShortlisted/","../data/"+folder_commentRelevance,"../data/"+folder_commentLiked,"../data/"+folder_commentLikedRelevance,"../data/"+folder_commentfirstNdays]

	annotateResult ={}
	
	vid_list=list()
	
	videofVector = {}
	commentsfVector = {}
	channelfVector = {}

	with open(annotateFile) as f:
		annotateResult = json.load(f)
	
	with open(argv[1]) as f:
		vid_list = f.readlines()
	for folder_comments in commentsFolderSet:
		FakeVideo = {}
		LegitVideo = {}
		folder_plots = "../data/Plots/"+folder_comments.split('/')[2]+"/"
		if not os.path.exists(folder_plots):
			os.makedirs(folder_plots)
		try:
			curr = 1
			for videoid in vid_list:
				if os.path.isfile(folder_videos + "Video_" + videoid.strip() + ".json") == False or os.path.isfile(folder_comments + "Video_" + videoid.strip() + ".json") == False or os.path.isfile(folder_channels + "Video_" + videoid.strip() + ".json") == False:
					continue
				print curr
				curr += 1
				try:
					videofVector = getVideoFeatures(folder_videos + "Video_" + videoid.strip() + ".json")
					commentsfVector = getCommentFeatures(folder_comments + "Video_" + videoid.strip() + ".json", videofVector["tags"],videofVector["publishedAt"],1)
					if commentsfVector == -1:
						continue
					# print commentsfVector['inappropriate_score']
					# print commentsfVector['jaccard_score']
					channelfVector = getChannelFeature(folder_channels + "Video_" + videoid.strip() + ".json")
					if curr == 2:
						getFeatureName(videofVector,commentsfVector,channelfVector)
					gatherAllFeature(annotateResult[videoid.strip()],videofVector,commentsfVector,channelfVector)
				except:
					continue
			normalizeFeature(int(argv[2]))
			plotFeatures(int(argv[2]))
		except:
			continue
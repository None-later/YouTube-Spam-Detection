import json
import os
import operator
from sys import argv

res = {}
count_exception = 0

def getDislikeLikeRatio(files):
	global res, count_exception
	try:
		with open("../data/VideoDetails/"+files,"r") as f:
			info = json.load(f);
			print info['items'][0]['statistics']
			res[files] = "("+str(float(info['items'][0]['statistics']['dislikeCount']) / float(info['items'][0]['statistics']['likeCount']))+","+str(info['items'][0]['statistics']['viewCount'])+")"
	except Exception as e:
		print files.strip(),":",e
		count_exception += 1
			

#python filename <videoIdsList>
if __name__ == '__main__':
	global res, count_exception
	with open(argv[1]) as f:
		for fname in f:
			getDislikeLikeRatio("Video_" + fname.strip() + ".json")
	sorted_list = sorted(res.items(), key=operator.itemgetter(1))
	output = open("../data/dislike_like_ratio_videos_threshold.txt","w")
	print "Total 0 like videos:", count_exception
	for item in sorted_list:
		print>>output, item
	output.close()

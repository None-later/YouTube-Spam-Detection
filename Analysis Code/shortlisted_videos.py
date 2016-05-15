import json
import os
import operator

res = {}

def getDislikeLikeRatio(vidList):
	global res
	for files in vidList:
		try:
			with open("../data/VideoDetails/Video"+str(files.strip())+".json","r") as f:
				info = json.load(f)
				if(int(info['items'][0]['statistics']['viewCount'])>50000):
					res[files] = float(info['items'][0]['statistics']['dislikeCount']) / float(info['items'][0]['statistics']['likeCount'])
		except Exception as e:
			print files.strip(),":",e
			


if __name__ == '__main__':
	global res
	for idx in range(1,15):
		fname = "../data/shortlisted_video"+str(idx)+".txt"
		vidList=list()
		with open(fname) as f:
			vidList = f.readlines()
		getDislikeLikeRatio(vidList)
	sorted_list = sorted(res.items(), key=operator.itemgetter(1))
	with open("../data/shortlisted_video_sorted_list_thresholding.txt","w") as output:
		output.write('\n'.join(sorted_list))


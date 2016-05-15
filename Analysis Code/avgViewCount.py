import os
import operator
import json
avg = 0.0
cnt = 0
for i in os.listdir("../data/VideoDetails"):
	try:
		with open("./../data/VideoDetails/"+i) as f:
			t = json.load(f)
			avg += float(t['items'][0]['statistics']['viewCount'])
			cnt += 1
	except Exception as e:
		print i," : ",e
		continue
avg /= cnt
print avg

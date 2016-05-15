# Ratio -> given as input (training test)
import numpy as np
from sys import argv
try:
	if argv[1] == 0 or argv[2] == 0:
		print "Invalid Input"
		exit()
except Exception,e:
	print "Provide Split-Ratio"

folder = "./useCommentLikedRelevanceFeature/"
X = np.load(folder + "X-Vector.npy")
Y = np.load(folder + "Y-Vector.npy")

positiveSet_size = len(Y[Y==1])
negativeSet_size = len(Y[Y==0])
# negativeSet_size = positiveSet_size


Training_size = int(argv[1]) * (positiveSet_size + negativeSet_size) / (int(argv[1]) + int(argv[2]))
Test_size = (positiveSet_size + negativeSet_size) - Training_size

positiveTraining_size = int(argv[1]) * (positiveSet_size) / (int(argv[1]) + int(argv[2]))
negativeTraining_size = int(argv[1]) * (negativeSet_size) / (int(argv[1]) + int(argv[2]))

positiveTest_size = positiveSet_size - positiveTraining_size
negativeTest_size = negativeSet_size - negativeTraining_size

X_Training = list()
Y_Training = list()
X_Test = list()
Y_Test = list()

cnt_TrainingPositive = 0
cnt_TrainingNegative = 0
cnt_TestPositive = 0
cnt_TestNegative = 0

print Training_size, Test_size, positiveSet_size, negativeSet_size

# X = [ np.append(val[4:46],val[412:429]) for val in X ]

for idx in range(len(Y)):
	if len(X[idx]) != max([len(X[i]) for i in range(len(X))]):
		continue
	if Y[idx] == 1:
		if cnt_TrainingPositive < positiveTraining_size:
			cnt_TrainingPositive += 1
			Y_Training += [ Y[idx] ]
			X_Training += [ X[idx] ]
		else:
			if cnt_TestPositive < positiveTest_size:
				cnt_TestPositive += 1
				Y_Test += [ Y[idx] ]
				X_Test += [ X[idx] ]
	elif Y[idx] == 0:
		 if cnt_TrainingNegative < negativeTraining_size:
			cnt_TrainingNegative += 1
			Y_Training += [ Y[idx] ]
			X_Training += [ X[idx] ]
		 else:
			if cnt_TestNegative < negativeTest_size:
				cnt_TestNegative += 1
				Y_Test += [ Y[idx] ]
				X_Test += [ X[idx] ]

			
np.save(folder + "X-Vector-Training",X_Training)
np.save(folder + "Y-Vector-Training",Y_Training)
np.save(folder + "X-Vector-Testing",X_Test)
np.save(folder + "Y-Vector-Testing",Y_Test)

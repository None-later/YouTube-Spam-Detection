# Stratified K fold. k is specified as input
from sys import argv 
import numpy as np
import matplotlib.pyplot as plt
from sklearn.cross_validation import KFold, StratifiedKFold as SKFold, ShuffleSplit as S_Split, StratifiedShuffleSplit as SS_Split
from sklearn import svm
from sklearn.ensemble import RandomForestClassifier
from sklearn.ensemble import AdaBoostClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.decomposition import PCA
from sklearn.feature_selection import SelectKBest
from sklearn.feature_selection import chi2
from sklearn.metrics import classification_report
from sklearn.metrics import precision_recall_curve
from sklearn.metrics import average_precision_score
from sklearn.cross_validation import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import FeatureUnion
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction import DictVectorizer
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn import cross_validation
from sklearn.naive_bayes import MultinomialNB
from sklearn.ensemble import RandomForestClassifier as RF

try:
	k = int(argv[1])
except Exception,e:
	print "Provide k for K-fold"
folder_train = "./usingVideoFeature/"
folder_test = "./usingVideoFeature_test/"
X_Training = np.load(folder_train + "X-Vector-Training.npy")
Y_Training = np.load(folder_train + "Y-Vector-Training.npy")
X_Testing = np.load(folder_test + "X-Vector.npy")
featureName = np.load(folder_train + "Features-Name.npy")

def rFfeatureImportance(clf):
	importances = clf.feature_importances_
	std = np.std([tree.feature_importances_ for tree in clf.estimators_],axis=0)
	indices = np.argsort(importances)[::-1]

	# Print the feature ranking
	print("Feature ranking:")
	for f in range(min(1000,len(featureName))):
	    print("%d. feature %s (%f)" % (f + 1, featureName[indices[f]], importances[indices[f]]))

def useRandomForest():
	print "\nUsing Random Forest:"

	clf = RandomForestClassifier(n_estimators=100)
	clf.fit(X_Training, Y_Training)
	print "\nClassification Report:\n"
	prediction = clf.predict(X_Testing)
	for i in prediction:
		print i

#Call as python <name of file> K-fold-val <yes/no>PCA <#componentsPCA>
if __name__ == '__main__':

	print "Report of dataset:"
	print "Training:-"
	print "Spam : ",len(Y_Training[Y_Training == 1])
	print "Legitimate : ",len(Y_Training[Y_Training == 0])
	
	try:
		if argv[2] == "yes":
			usePCA(int(argv[3]))
	except Exception,e:
		print "Provide yes/no option & number of components to use for PCA"
	useRandomForest()

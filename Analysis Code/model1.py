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
from sklearn.metrics import classification_report,confusion_matrix
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
import math
try:
	k = int(argv[1])
except Exception,e:
	print "Provide k for K-fold"
folder = "./top650_modified/"
X_Training = np.load(folder + "X-Vector-Training.npy")
Y_Training = np.load(folder + "Y-Vector-Training.npy")
X_Testing = np.load(folder + "X-Vector-Testing.npy")
Y_Testing = np.load(folder + "Y-Vector-Testing.npy")
featureName = np.load(folder + "Features-Name.npy")
X = np.load(folder + "X-Vector.npy")
Y = np.load(folder + "Y-Vector.npy")
X = np.append(X_Training,X_Testing,axis=0)
Y = np.append(Y_Training,Y_Testing)
balancing="balanced"

def rFfeatureImportance(clf):
	importances = clf.feature_importances_
	std = np.std([tree.feature_importances_ for tree in clf.estimators_],axis=0)
	indices = np.argsort(importances)[::-1]

	# Print the feature ranking
	print("Feature ranking:")

	for f in range(10):
		print("%d. feature %s (%f)" % (f + 1, featureName[indices[f]], importances[indices[f]]))

def useKFoldSVM():
	# global X_Training
	# global X_Testing
	print "\nUsing SVM:"

	# X_Training = SelectKBest(chi2, k=400).fit_transform(X_Training, Y_Training)
	# X_Testing = SelectKBest(chi2, k=400).fit_transform(X_Testing, Y_Testing)
	print "Total Size:-",len(Y)
	skf = SKFold(Y, n_folds = k, shuffle=True)
	for train, test in skf:
			#print train, test
			X_train, Y_train = [X[i] for i in train], [Y[i] for i in train]
			X_test, Y_test =  [X[i] for i in test], [Y[i] for i in test]
			Y_train = np.array(Y_train)
			X_train = np.array(X_train)
			Y_test = np.array(Y_test)
			X_test = np.array(X_test)
			print "Training:-"
			print "Fake : ",len(Y_train[Y_train==1])
			print "Legitimate : ",len(Y_train[Y_train==0])

			print "Testing:-"
			print "Fake : ",len(Y_test[Y_test==1])
			print "Legitimate : ",len(Y_test[Y_test==0])
			clf = svm.SVC(C=1.0)
			clf.fit(X_train, Y_train)
			print "No weightage Given\nAccuracy: ", clf.score(X_test,Y_test)
			print "\nClassification Report:\n",classification_report(Y_test, clf.predict(X_test),target_names=["Legitimate","Fake"])
			# rFfeatureImportance(clf)
			# ratio = len(Y_train[Y_train==0])/len(Y_train[Y_train==1])
			# wtg = np.array([1 if i == 1 else 1 for i in Y_train])
			# wclf = svm.SVC(C=1.0,class_weight = balancing)
			# wclf.fit(X_train, Y_train,sample_weight = wtg)
			# print "Weightage Given\nAccuracy: ", wclf.score(X_test,Y_test)
			# rFfeatureImportance(wclf)

			# print "\nClassification Report:\n",classification_report(Y_test, wclf.predict(X_test),target_names=["Legitimate","Fake"])

def useKFoldRandomForest():
	print "\nUsing Random Forest:"

	print "Total Size:-",len(Y)
	skf = SKFold(Y, n_folds = k, shuffle=True)
	for train, test in skf:
			#print train, test
			X_train, Y_train = [X[i] for i in train], [Y[i] for i in train]
			X_test, Y_test =  [X[i] for i in test], [Y[i] for i in test]
			Y_train = np.array(Y_train)
			X_train = np.array(X_train)
			Y_test = np.array(Y_test)
			X_test = np.array(X_test)
			print "Training:-"
			print "Fake : ",len(Y_train[Y_train==1])
			print "Legitimate : ",len(Y_train[Y_train==0])

			print "Testing:-"
			print "Fake : ",len(Y_test[Y_test==1])
			print "Legitimate : ",len(Y_test[Y_test==0])
			clf = RandomForestClassifier(n_estimators=100)
			clf.fit(X_train, Y_train)
			print "No weightage Given\nAccuracy: ", clf.score(X_test,Y_test)
			print "\nClassification Report:\n",classification_report(Y_test, clf.predict(X_test),target_names=["Legitimate","Fake"])
			# rFfeatureImportance(clf)
			# ratio = len(Y_train[Y_train==0])/len(Y_train[Y_train==1])
			# wtg = np.array([1 if i == 1 else 1 for i in Y_train])
			# wclf = RandomForestClassifier(n_estimators=100,class_weight=balancing)
			# wclf.fit(X_train, Y_train,sample_weight = wtg)
			# print "Weightage Given\nAccuracy: ", wclf.score(X_test,Y_test)
			# # rFfeatureImportance(wclf)

			# print "\nClassification Report:\n",classification_report(Y_test, wclf.predict(X_test),target_names=["Legitimate","Fake"])

def useKFoldDecisionTree():
	print "\nUsing Decision Tree:"

	print "Total Size:-",len(Y)
	skf = SKFold(Y, n_folds = k, shuffle=True)
	for train, test in skf:
			#print train, test
			X_train, Y_train = [X[i] for i in train], [Y[i] for i in train]
			X_test, Y_test =  [X[i] for i in test], [Y[i] for i in test]
			Y_train = np.array(Y_train)
			X_train = np.array(X_train)
			Y_test = np.array(Y_test)
			X_test = np.array(X_test)
			print "Training:-"
			print "Fake : ",len(Y_train[Y_train==1])
			print "Legitimate : ",len(Y_train[Y_train==0])

			print "Testing:-"
			print "Fake : ",len(Y_test[Y_test==1])
			print "Legitimate : ",len(Y_test[Y_test==0])
			clf = DecisionTreeClassifier()
			clf.fit(X_train, Y_train)
			print "No weightage Given\nAccuracy: ", clf.score(X_test,Y_test)
			print "\nClassification Report:\n",classification_report(Y_test, clf.predict(X_test),target_names=["Legitimate","Fake"])
			# rFfeatureImportance(clf)
			# ratio = len(Y_train[Y_train==0])/len(Y_train[Y_train==1])
			# wtg = np.array([1 if i == 1 else 1 for i in Y_train])
			# wclf = DecisionTreeClassifier(class_weight=balancing)
			# wclf.fit(X_train, Y_train,sample_weight = wtg)
			# print "Weightage Given\nAccuracy: ", wclf.score(X_test,Y_test)
			# # rFfeatureImportance(wclf)

			# print "\nClassification Report:\n",classification_report(Y_test, wclf.predict(X_test),target_names=["Legitimate","Fake"])

def useKFoldAdaBoostClassifier():
	print "\nUsing AdaBoostClassifier:"

	print "Total Size:-",len(Y)
	skf = SKFold(Y, n_folds = k, shuffle=True)
	for train, test in skf:
			#print train, test
			X_train, Y_train = [X[i] for i in train], [Y[i] for i in train]
			X_test, Y_test =  [X[i] for i in test], [Y[i] for i in test]
			Y_train = np.array(Y_train)
			X_train = np.array(X_train)
			Y_test = np.array(Y_test)
			X_test = np.array(X_test)
			print "Training:-"
			print "Fake : ",len(Y_train[Y_train==1])
			print "Legitimate : ",len(Y_train[Y_train==0])

			print "Testing:-"
			print "Fake : ",len(Y_test[Y_test==1])
			print "Legitimate : ",len(Y_test[Y_test==0])
			clf = AdaBoostClassifier()
			clf.fit(X_train, Y_train)
			print "No weightage Given\nAccuracy: ", clf.score(X_test,Y_test)
			print "\nClassification Report:\n",classification_report(Y_test, clf.predict(X_test),target_names=["Legitimate","Fake"])
			# rFfeatureImportance(clf)
			# ratio = len(Y_train[Y_train==0])/len(Y_train[Y_train==1])
			# wtg = np.array([1 if i == 1 else 1 for i in Y_train])
			# wclf = AdaBoostClassifier()
			# wclf.fit(X_train, Y_train,sample_weight = wtg)
			# print "Weightage Given\nAccuracy: ", wclf.score(X_test,Y_test)
			# # rFfeatureImportance(wclf)

			# print "\nClassification Report:\n",classification_report(Y_test, wclf.predict(X_test),target_names=["Legitimate","Fake"])

def usePCA(n):
	print "\nUsing PCA with components:",n
	global X_Testing
	global X_Training
	pca = PCA(n_components=n)# adjust yourself
	pca.fit(X_Training)
	X_Training = pca.transform(X_Training)
	X_Testing = pca.transform(X_Testing)

#Call as python <name of file> K-fold-val <yes/no>PCA <#componentsPCA>
if __name__ == '__main__':

	# print "Report of dataset:"
	# print "Training:-"
	# print "Fake : ",len(Y_Training[Y_Training == 1])
	# print "Legitimate : ",len(Y_Training[Y_Training == 0])

	# print "Testing:-"
	# print "Fake : ",len(Y_Testing[Y_Testing == 1])
	# print "Legitimate : ",len(Y_Testing[Y_Testing == 0])
	
	try:
		if argv[2] == "yes":
			usePCA(int(argv[3]))
	except Exception,e:
		print "Provide yes/no option & number of components to use for PCA"
	# useKFoldSVM()
	# useKFoldRandomForest()
	useKFoldDecisionTree()
	# useKFoldAdaBoostClassifier()

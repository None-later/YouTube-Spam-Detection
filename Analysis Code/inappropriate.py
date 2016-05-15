import sys
import nltk
import re
import pprint
from nltk.corpus import stopwords
from nltk import word_tokenize
from nltk.stem.wordnet import WordNetLemmatizer
stop = stopwords.words('english')
lemma=WordNetLemmatizer()

file_swear="./BOW Files/swear_final_lemma.txt"
swear_words=[]
def init():
	global swear_words
	with open(file_swear) as f:
		swear_words=f.readlines()
	swear_words=[words.strip(" \r\n\t").lower() for words in swear_words]
def call(answer):
	global swear_words
	count_sword=0
	count_total=0
	answer = re.sub(r'[^\w]',' ',answer)
	tokens = word_tokenize(answer)
	tokens = [word.lower().strip(" \r\n\t") for word in tokens]
	if len(tokens) > 0:
		count_total = count_total+2*len(tokens) - 1
	for word in tokens:
		if len(word) == 1 or word in stop:
			continue
		word = lemma.lemmatize(word)
		if word in swear_words:
			count_sword += 1
	for i in range(len(tokens) - 1):
		word_curr = tokens[i]
		word_next = tokens[i+1]
		if len(word_curr) == 1 or word_curr in stop:
			continue
		word_bi=word_curr + word_next
		if word_bi in swear_words:
			count_sword += 1
	if count_total == 0:
		return 0.0
	return (count_sword*100.0)/count_total

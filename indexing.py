import json
import json
import re
import csv
import pprint
import nltk.classify
import pickle
import time
from datetime import datetime
import os
os.environ['TZ'] = 'Asia/Jakarta'
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
import requests
from elasticsearch import Elasticsearch
es= Elasticsearch()


access_token = "994846208-9JBpqUCyGqmDu4aNVBzrO72v6azLQJMg6FykuA1l"
access_token_secret = "ZrJdUIibacKNQlF7FkYPi2aont1RMEJJ0As2gwlzUFRaw"
consumer_key = "J4bmMjlS7DLZMQaVvHChByrvi"
consumer_secret = "hp840RBNliVYrnfnqpVHXvpOij2cuQTDG72OpVYXasSSNc0fHY"



class TweetStreamListener(StreamListener):

    # on success
    def on_data(self, data):

        # decode json
        dict_data = json.loads(data)

	#start replaceTwoOrMore
	def replaceTwoOrMore(s):
    		#look for 2 or more repetitions of character
    		pattern = re.compile(r"(.)\1{1,}", re.DOTALL) 
    		return pattern.sub(r"\1\1", s)
	#end

	#start process_tweet
	def processTweet(tweet):
            	# lower
        	tweet = tweet.lower()
            	# remove non alphabetic character
		tweet = re.sub(r'(.)\1+', r'\1\1', tweet)#hapus pengulangan huruf
		tweet = re.sub(r'[^\x00-\x7f]',r' ',tweet)#hapus karakter aneh selain ascii
		tweet = re.sub(r"http\S+", "", tweet)# hapus url
		tweet = tweet.replace("("," ")
		tweet = tweet.replace(")"," ")
		tweet = tweet.replace("#"," ")
		tweet = tweet.replace("@"," ")
		tweet = tweet.replace("!","")
		tweet = tweet.replace("?","")
		tweet = re.sub(' +',' ',tweet)
		
		
        	# replace abbreviations
        	replacement_word_list = [line.rstrip('\n').rstrip('\r') for line in open('kataganti.txt')]

        	replacement_words = {}
        	for replacement_word in replacement_word_list:
            		replacement_words[replacement_word.split(',')[0]] = replacement_word.split(',')[1]

        	new_string = []
        	for word in tweet.split():
            		if replacement_words.get(word, None) is not None:
                		word = replacement_words[word]
            		new_string.append(word)

        	tweet = ' '.join(new_string)
        	return tweet
  		
	#end 

	#start getStopWordList
	def getStopWordList(stopWordListFileName):
    		#read the stopwords
    		stopWords = []
    		stopWords.append('at')
    		stopWords.append('with')

    		fp = open(stopWordListFileName, 'r')
    		line = fp.readline()
    		while line:
        		word = line.strip()
        		stopWords.append(word)
        		line = fp.readline()
    		fp.close()
    		return stopWords
	#end
	
	def objParwis(tweet,klas):
		tweet=tweet.replace("-"," ")
		tweet=tweet.replace(" ","")
		wordout=""
		if klas =="candi":
			list_candi=[line.strip() for line in open("listcandi.txt", 'r')]
			for word in list_candi:
				if word in tweet:
					wordout=word
		elif klas=="museum/sejarah":
			list_msm=[line.strip() for line in open("sejarahmuseum.txt", 'r')]
			for word in list_msm:
				if word in tweet:
					wordout=word
		elif klas=="wisatakeluarga":
			list_klg=[line.strip() for line in open("wisatakeluarga.txt", 'r')]
			for word in list_klg:
				if word in tweet:
					wordout=word
		elif klas=="wisataalam":
			list_alam=[line.strip() for line in open("wisataalam.txt", 'r')]
			for word in list_alam:
				if word in tweet:
					wordout=word
		elif klas=="pantai":
			list_pantai=[line.strip() for line in open("pantai.txt", 'r')]
			for word in list_pantai:
				if word in tweet:
					wordout=word
		elif klas=="desawisata":
			list_dwi=[line.strip() for line in open("desawisata.txt", 'r')]
			for word in list_dwi:
				if word in tweet:
					wordout=word
		return wordout
	#start getfeatureVector
	def getFeatureVector(tweet, stopWords):
    		featureVector = []  
    		words = tweet.split()
    		for w in words:
        		#replace two or more with two occurrences 
        		w = replaceTwoOrMore(w) 
        		#strip punctuation
        		w = w.strip('\'"?,.')
        		#check if it consists of only words
        		val = re.search(r"^[a-zA-Z][a-zA-Z0-9]*[a-zA-Z]+[a-zA-Z0-9]*$", w)
        		#ignore if it is a stopWord
        		if(w in stopWords or val is None):
            			continue
        		else:
            			featureVector.append(w.lower())
    		return featureVector    
	#end

	#start extract_features
	def extract_features(tweet):
    		tweet_words = set(tweet)
    		features = {}
    		for word in featureList:
        		features['contains(%s)' % word] = (word in tweet_words)
    		return features
	#end

	featureList = []
	#open the model classifier
	f = open('modelpariwisata9.pickle', 'rb')
	Classifier = pickle.load(f)
	f.close()

    # Test the classifier with tweet
	tweet = dict_data["text"]
	stopWords = getStopWordList('stopword.txt')
	processedtweet = processTweet(tweet)
	featureVector = getFeatureVector(processedtweet, stopWords)
	featureList.extend(featureVector)
	topik = Classifier.classify(extract_features(getFeatureVector(processedtweet, stopWords)))
	
	
	if topik != 'tidaktahu':
		obPar= objParwis(processedtweet,topik)
		savethis=("%s|%s|%s" % (topik,obPar,tweet))
		print savethis
		indek= {
		"time":datetime.now(),
		"class":topik,
		"tweet":tweet,
		"obj":obPar,
		}
		es.index(index="parwis",doc_type="doc", body=indek)
    # on failure
    def on_error(self, status):
        print status

if __name__ == '__main__':

    # create instance of the tweepy tweet stream listener
    listener = TweetStreamListener()

    # set twitter keys/tokens
    auth = OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)

    # create instance of the tweepy stream
    stream = Stream(auth, listener)
#stream.filter(locations=[109.6667,-8.5,111,-7.3333])
#stream.filter(locations=[110.006126,-8.20693,110.83947,-7.54178])
stream.filter(locations=[110.006126,-8.20693,110.83947,-7.54178])

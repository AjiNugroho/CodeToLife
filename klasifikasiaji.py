#import regex
import re
import csv
import pprint
import nltk.classify
import pickle

from sklearn.naive_bayes import BernoulliNB
from sklearn.svm import LinearSVC
from sklearn.tree import DecisionTreeClassifier
from nltk.tag import tnt

#start replaceTwoOrMore
def replaceTwoOrMore(s):
    #look for 2 or more repetitions of character
    pattern = re.compile(r"(.)\1{1,}", re.DOTALL) 
    return pattern.sub(r"\1\1", s)
#end

#start process_tweet
def processTweet(tweet):
    # process the tweets
    
    #Convert to lower case
	tweet = tweet.lower()
	tweet = re.sub(r'[^\x00-\x7f]',r' ',tweet)#hapus karakter aneh selain ascii
	tweet = re.sub(r"http\S+", "", tweet)# hapus url
	tweet = tweet.replace("("," ")
	tweet = tweet.replace(")"," ")
	tweet = tweet.replace("#"," ")
	tweet = tweet.replace("@"," ")
	tweet = tweet.replace("_"," ")
	tweet = re.sub(' +',' ',tweet)
#	tweet = re.sub(r'(.)\1+', r'\1\1', tweet)#hapus pengulangan huruf
#	tweet = re.sub(r"http\S+", "", tweet)# hapus url
#	regex = re.compile('@[a-zA-Z0-9_]+')#hapus @
#	tweet = regex.sub(' ', tweet)
#	regex = re.compile('RT\s')#hapus rt
#	tweet = regex.sub(' ', tweet)
#	regex = re.compile('[^a-zA-Z0-9]')#hapus selain huruf kata dll
#	tweet = regex.sub(' ', tweet)
#	tweet = re.sub(r'[^\w]', ' ', tweet)#hapus tanda baca
	    #trim
	return tweet
	#end 

#start getStopWordList
def getStopWordList(stopWordListFileName):
    #read the stopwords
    stopWords = []
    

    fp = open(stopWordListFileName, 'r')
    line = fp.readline()
    while line:
        word = line.strip()
        stopWords.append(word)
        line = fp.readline()
    fp.close()
    return stopWords
#end

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


#Read the tweets one by one and process it
inpTweets = csv.reader(open('pariwisatajogja8.csv', 'rb'), delimiter=',', quotechar='"')
stopWords = getStopWordList('stopword.txt')
count = 0;
featureList = []
tweets = []
for row in inpTweets:
	topik = row[0]
    	tweet = row[1]
    	processedTweet = processTweet(tweet)
	featureVector = getFeatureVector(processedTweet, stopWords)
    	featureList.extend(featureVector)
    	tweets.append((featureVector, topik));
#end loop

# Remove featureList duplicates
featureList = list(set(featureList))

# Generate the training set
training_set = nltk.classify.util.apply_features(extract_features, tweets)


# Train the classifier
Classifier = nltk.classify.SklearnClassifier(LinearSVC(max_iter=10000)).train(training_set)
f = open('modelpariwisata9.pickle', 'wb')
pickle.dump(Classifier, f)
f.close()

'''
    @date 12/14/19
    @author lefko
    @summary accessing and filtering tweets using python
    https://realpython.com/twitter-bot-python-tweepy/
'''

import csv
import re
import json
import pprint
import tweepy
import os
import nltk
import pandas as pd
from tinydb import TinyDB

# for handling many tweets at once
from queue import Queue
from threading import Thread

class TwitterUrbanHealth():

    def __init__(self, num_tweets = 10000):
        super().__init__()
        self.__loadTokens__()
        self.__accessTwitterAPI__()
        self.__num_tweets__ = 10000

    def __loadTokens__(self):

        self.twitter_creds = {} # credentials
        with open('./twitterapi_creds.py') as creds:
            for line in creds:
                key, val = line.split("=")
                self.twitter_creds[key.strip()] = val.replace('\n', '').replace('"', '').strip()

        print(self.twitter_creds)

    def __accessTwitterAPI__(self):
        self.auth = tweepy.OAuthHandler(self.twitter_creds['API_KEY'], self.twitter_creds['API_SECRET_KEY'])
        self.auth.set_access_token(self.twitter_creds['ACCESS_TOKEN'], self.twitter_creds['ACCESS_TOKEN_SECRET'])

        self.api = tweepy.API(self.auth, wait_on_rate_limit = True, wait_on_rate_limit_notify = True) # and access the API itself

        return self.api

    def __loadKeywords__(self, path = '../data/keywords.txt'):
        '''
            load keywords related to 'disease'
        '''
        keywords = []
        with open(path) as txt:
            for line in txt:
                keywords.append(line.strip())

        print(str(len(keywords)), ' keywords loaded!')
        return keywords

    def getAPIHandle(self):
        return self.api

    def startListen(self, loc = None, useTrack = True, max_tweets = 10000, debug=False):
        '''
            @param loc: The location is a rectangle whose first two coordinates (longitude and latitude) are the bottom left corner and the last two are the top right corner
        '''
        print('streamign tweets for', loc)

        stream = tweepy.Stream(auth = self.api.auth, listener = StreamListener(maxTweets = max_tweets, debug = debug))
        
        '''
            @track filter for tweets containing certain words
            @languagese well, obvious
            @locations 
            @is_async run stream in new thread

            ??? cannot apply both track AND locations
        '''
        if(useTrack == True):
            stream.filter(track = self.__loadKeywords__(), languages = ['en'], is_async = True)
        else:
            stream.filter(locations = loc, languages = ['en'], is_async = True)

    def crawlTweets(self, username):
        crawler = TweetCrawler('12/19/19', '09/01/19', self.api)
        crawler.crawlUser('')

class TweetCrawler():
    """
        crawls all tweets for a given user between to specific dates
        https://gist.github.com/alexdeloy/fdb36ad251f70855d5d6
    """

    def __init__(self, api):
        self.user_tweets = []
        self.filtered_tweets = []
        #self.from_date = datetime.strptime(from_date, '%m/%d/%y')
        #self.to_date = datetime.strptime(to_date, '%m/%d/%y')

        # tweepy API handle
        self.api = api

    def crawlUser(self, username, from_date, to_date):
        self.user_tweets = self.api.user_timeline(username)
        self.from_date = datetime.strptime(from_date, '%m/%d/%y')
        self.to_date = datetime.strptime(to_date, '%m/%d/%y')
        
        for tw in self.user_tweets:
            if tw.created_at > self.from_date and tw.created_at < self.to_date:
                self.filtered_tweets.append(tw)

        return self.user_tweets

    def crawlTweets(self, keywords, loc = None):
        # geocode="5.29126, 52.132633, 600km"
        # Denver: 39.778889, -104.9825
        if loc != None:
            keywords = '*'
        
        for tweet in self.api.search(q = keywords, lang = "en", geocode = loc):
            print(f"{tweet.user.name}:{tweet.text}")


class StreamListener(tweepy.StreamListener):

    def __init__(self, maxTweets, debug = False, q = Queue()):
        self.numTweets = 0
        self.maxTweets = maxTweets
        self.twDao = TweetDAO.getInstance(mode='csv')
        self.debug = debug
        self.q = q

        #for i in range(4):
        #    t = Thread(target=self.processTweet)
        #    t.daemon = True
        #    t.start()

        print('set maxTweets = ',self.maxTweets)

        super(StreamListener, self).__init__()

    def on_status(self, status):
        if hasattr(status, 'retweeted_status'):
            # ignore retweets, bc. they are too noisy
            return

        #print(status.text) # print any text coming from the API

        if self.numTweets > self.maxTweets:
            print('stopping the StreamListener')
            return False
        else:
            if(self.debug == False):
                self.processTweet(status)
                #self.q.put(status) # put the new tweet in the queue
            else:
                print(status)


    def on_error(self, status_code):
        if status_code == 420:
            return False

    def processTweet(self, status = None):
        '''
            status is a wrapper for all tweet-related properties, e.g. user, text, location
        
        description = status.user.description
        loc = status.user.location
        text = status.text
        coords = status.coordinates
        name = status.user.screen_name
        user_created = status.user.created_at
        followers = status.user.followers_count
        id_str = status.id_str
        created = status.created_at
        retweets = status.retweet_count
        bg_color = status.user.profile_background_color
        '''
        #while True:
        #    status = self.q.get()
        loc = ''
        if (status.user.location != None):
            loc = re.sub('[^A-Za-z0-9]+', ' ', status.user.location)
        tweet = {'id':status.id_str, 'created':status.created_at.isoformat(), 'loc':loc, 
        'text':status.text}

        self.twDao.writeToCSV(tweet)
        self.numTweets += 1

        #self.q.task_done()

class TweetDAO():
    """
    """
    __instance = None
    @staticmethod
    def getInstance(mode):
        if TweetDAO.__instance is None:
            TweetDAO(mode)
        return TweetDAO.__instance

    def getDBName(self):
        return self.dbFile

    def __init__(self, mode = 'json'):
        self.dbFile = '../db/tweets.' + mode
        TweetDAO.__instance = self

        if(mode == 'json'):
            # check if the db file already exists
            if(os.path.isfile(self.dbFile) == False):
                self.db = TinyDB(self.dbFile)
            else:
                print('TinyDB already initiated!')
                self.db = TinyDB(self.dbFile)
        elif(mode == 'csv'):
            pass

    def writeToCSV(self, tweet):
        print('Saving new Tweet:', tweet)
        with open(self.dbFile, mode='a') as tweets_file:
            #fieldnames = ['id_str', 'created_at', 'location', 'text']
            tweets_writer = csv.writer(tweets_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            tweets_writer.writerow([tweet['id'], tweet['created'], tweet['loc'], tweet['text']])

    def save(self, tweet):
        print('Saving new Tweet:', tweet)
        self.db.insert(tweet)
    
    def getAll(self):
        return self.db.all()

    def get(self, docId):
        return self.db.get(doc_id = docId)

    def JSONToDF(self):
        """
            convert db records to a pandas dataframe
        """
        df = pd.DataFrame()
        self.tweets = self.db.all()
        for i, tweet in enumerate(self.tweets):
            df = df.append(pd.DataFrame(tweet, index = [i]))

        print(df)
        return df

class TweetProcessor():
    """
        process a tweet, e.g. apply some NLP to extract relevant information from it
    """
    def __init__(self):
        self.dao = TweetDAO.getInstance(mode = 'csv')
        self.tweets_raw = self.dao.getAll()

    def showSummary(self):
        #print(len(self.tweets_raw))
        #print(self.tweets_raw[0])
        self.tweets = self.dao.JSONToDF()
        print(self.tweets.head())

    def process(self, tweetText):
        porter = nltk.PorterStemmer()
        tokens = nltk.word_tokenize(tweetText) # create a list of tokens from the raw text
        text = nltk.Text(tokens) # creates an NLTK text object
        word = [w.lower() for w in text] # normalization, i.e. lowercasing

        stemmedTokens = [porter.stem(t) for t in tokens]

    def readJSON(self):
        """
            read the db.json file and convert it to a pandas dataframe
        """
        # reading the JSON data using json.load()
        with open(self.dao.getDBName()) as train_file:
            dict_tweets = json.load(train_file)

        # converting json dataset from dictionary to dataframe
        train = pd.DataFrame.from_dict(dict_tweets)
        #train.reset_index(level=0, inplace=True)
        print(train.head())
        print(train.tail())
        print(len(train))
        print(train[0])

if __name__ == "__main__":
    tuh = TwitterUrbanHealth()
    #tc = TweetCrawler(api = tuh.getAPIHandle())
    #tc.crawlTweets('python', loc = '39.778889, -104.9825, 600km') # Denver
    #tc.crawlTweets('python')
    # https://boundingbox.klokantech.com/
    colorado = [-109.51,36.81,-101.51,41.01]
    massachussetts = [-74.16,40.92,-69.62,43.09]
    california = [-126.02,31.45,-114.31,42.197]
    usa = [-125.55,27.75,-66.05,48.93]
    tuh.startListen(loc = california, useTrack=False, max_tweets=50000)

    # after recording tweets we'll continue with processing them
    #tp = TweetProcessor()
    #tp.showSummary()
    #tp.readJSON()
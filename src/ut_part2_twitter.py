'''
    @date 12/14/19
    @author lefko
    @summary accessing and filtering tweets using python
    https://realpython.com/twitter-bot-python-tweepy/
'''

import tweepy
import os
import nltk
from tinydb import TinyDB

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

    def startListen(self, filter, loc):
        '''
            @param loc: The location is a rectangle whose first two coordinates (longitude and latitude) are the bottom left corner and the last two are the top right corner
        '''

        stream = tweepy.Stream(auth = self.api.auth, listener = StreamListener(maxTweets = 1000))
        stream.filter(track = self.__loadKeywords__(), languages = ['en'], locations = loc, is_async = True) # use track for applying filter terms to the stream

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

    def __init__(self, maxTweets):
        self.numTweets = 0
        self.maxTweets = maxTweets
        self.twDao = TweetDAO()

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
            self.processTweet(status)


    def on_error(self, status_code):
        if status_code == 420:
            return False

    def processTweet(self, status):
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
        
        tweet = {'id':status.id_str, 'created':status.created_at.isoformat(), 
        'user':status.user.screen_name, 'coords':status.coordinates, 'loc':status.user.location, 
        'text':status.text}

        self.twDao.save(tweet)
        self.numTweets += 1

class TweetDAO():
    """
    """
    __instance = None
    @staticmethod
    def getInstance():
        if TweetDAO.__instance is None:
            TweetDAO()
        return TweetDAO.__instance

    def __init__(self):
        self.dbFile = '../db/tweets.json'
        TweetDAO.__instance = self

        # check if the db file already exists
        if(os.path.isfile(self.dbFile) == False):
            self.db = TinyDB(self.dbFile)
        else:
            print('TinyDB already initiated!')
            self.db = TinyDB(self.dbFile)

    def save(self, tweet):
        print('Saving new Tweet:', tweet)
        self.db.insert(tweet)
    
    def getAll(self):
        return self.db.all()

    def get(self, docId):
        return self.db.get(doc_id = docId)

class TweetProcessor():
    """
        process a tweet, e.g. apply some NLP to extract relevant information from it
    """
    def __init__(self, dao):
        self.tweets_raw = self.dao.getAll()

    def process(self, tweetText):
        porter = nltk.PorterStemmer()
        tokens = nltk.word_tokenize(tweetText) # create a list of tokens from the raw text
        text = nltk.Text(tokens) # creates an NLTK text object
        word = [w.lower() for w in text] # normalization, i.e. lowercasing

        stemmedTokens = [porter.stem(t) for t in tokens]


if __name__ == "__main__":
    tuh = TwitterUrbanHealth()
    #tc = TweetCrawler(api = tuh.getAPIHandle())
    #tc.crawlTweets('python', loc = '39.778889, -104.9825, 600km') # Denver
    #tc.crawlTweets('python')
    tuh.startListen(filter = None, loc = [-109.165421, 36.886651, -102.137268, 40.787197]) # should be Colorado
    #tuh.startListen(['johnson', 'trump'])
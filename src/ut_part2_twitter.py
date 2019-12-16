'''
    @date 12/14/19
    @author lefko
    @summary accessing and filtering tweets using python
    
'''

import tweepy
import os
from tinydb import TinyDB

class TwitterUrbanHealth():

    def __init__(self):
        super().__init__()
        self.__loadTokens__()

    def __loadTokens__(self):

        self.twitter_creds = {} # credentials
        with open('./twitterapi_creds.py') as creds:
            for line in creds:
                key, val = line.split("=")
                self.twitter_creds[key.strip()] = val.replace('\n', '').replace('"', '')

        print(self.twitter_creds)

    def __authWithTwitter__(self):
        self.auth = tweepy.OAuthHandler(self.twitter_creds['API_KEY'], self.twitter_creds['API_SECRET_KEY'])
        self.auth.set_access_token(self.twitter_creds['ACCESS_TOKEN'], self.twitter_creds['ACCESS_TOKEN_SECRET'])

        self.api = tweepy.API(self.auth) # and access the API itself

        return self.api.auth

    def startListen(self, filter):
        stream = tweepy.Stream(auth = self.__authWithTwitter__(), listener = StreamListener())
        stream.filter(track = filter)


class StreamListener(tweepy.StreamListener):

    def on_status(self, status):
        if hasattr(status, 'retweeted_status'):
            # ignore retweets, bc. they are too noisy
            return

        #print(status.text) # print any text coming from the API
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
        self.twDao = TweetDAO()
        tweet = {'id':status.id_str, 'created':status.created_at.isoformat(), 
        'user':status.user.screen_name, 'coords':status.coordinates, 'loc':status.user.location, 
        'text':status.text}

        self.twDao.save(tweet)

class TweetDAO():
    def __init__(self):
        self.dbFile = '../db/tweets.json'
        
        # check if the db file already exists
        if(os.path.isfile(self.dbFile) == False):
            self.db = TinyDB(self.dbFile)
        else:
            print('TinyDB already initiated!')
            self.db = TinyDB(self.dbFile)

    def save(self, tweet):
        print('Saving new Tweet:', tweet)
        self.db.insert(tweet)


if __name__ == "__main__":
    tuh = TwitterUrbanHealth()
    tuh.startListen(['influenza', 'dengue', 'vaccination', 'mortal'])
    #tuh.startListen(['johnson', 'trump'])
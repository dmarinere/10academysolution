
from __future__ import absolute_import

#import tweepy, the python library that interacts with Twitter API.
import tweepy
import time
import os
#import psycopg2 for managing our postgresql database
import psycopg2

#postgrSQL data integration
DATABASE_URL = os.environ['DATABASE_URL']


# Go to http://apps.twitter.com and create an app.
# The consumer key and secret will be generated for you after.



#these are the keywords we intend to stream, you can add additional ones by placing a comma(,) after the last keyword.
keyword_to_stream = ['BBNaija',
                     'laycon',
                     '#bbnaija2020',
                     'nengi']

#Here we create a class that initiates the streaming proccess.


class StdOutListener(tweepy.StreamListener):
    """ A listener handles tweets that are received from the stream.
    This is a basic listener that prints received tweets to stdout and adds to DB.
    """
    #We define how things should go if they work out well

    def on_status(self, status):
        print(status.text)
        #print(status.id)
        print("\n")
        text = status.text
        url = "https://twitter.com/user/status/" + str(status.id)
        try:
            #To fade out retweets since we might have added the initial Tweet, and do not need
            if text.startswith('RT'):
                print('Tweet Skipped. This is a retweet')
                pass

            else:
                try:
                    #db integration
                    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
                    cursor = conn.cursor()
                    sql_insert_query = """ INSERT INTO bbnaija2020 (TWEET_LINK, USERNAME, TWEET, TIME) VALUES (%s,%s,%s,%s) """
                    record_to_insert = (
                        url, status.user.screen_name, status.text, status.created_at)
                    cursor.execute(sql_insert_query, record_to_insert)
                    conn.commit()
                    print(cursor.rowcount,
                          "Record inserted successfully into Twitter table")

                except (Exception, psycopg2.Error) as error:
                    print(
                        "Failed inserting record into Twitter table, tweet already logged. {}".format(error))

                finally:
                    # closing database connection.
                    if (conn):
                        cursor.close()
                        conn.close()
                        #print("PostgreSQL connection is closed")

        #if there's an error, most likely due to rate limit reached, script will sleep for 200 minutes
        except tweepy.TweepError as e:
            print('Time to sleep')
            time.sleep(200 * 60)
            StdOutListener(tweepy.StreamListener)

    #if there's an error reading twitter, say their stream ended or any internal error, script would sleep and rerun in 10 minutes
    def on_error(self, status):
        print('Stream ended, restarting')
        time.sleep(60 * 10)
        StdOutListener(tweepy.StreamListener)


if __name__ == '__main__':
    l = StdOutListener()
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth)
    stream = tweepy.Stream(auth, l)
    stream.filter(track=keyword_to_stream)

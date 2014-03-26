#! /usr/bin/env python3
# coding: utf-8
import json
import smtplib
import sqlite3
import sys
import traceback
import urllib.request
from TwitterAPI import TwitterAPI

# Credentials are saved in .json configuration file.  Obtain your credentials
#  from dev.twitter.com.
with open('credentials.json','r') as credentials_file:
    creds = json.load(credentials_file)
    # email = creds['email']
    # password = creds['password']
    # smtp_server = creds['smtp_server']
    # phone = creds['phone_number']
    # carrier = creds['carrier']

# Keywords & locations to filter the tweets by
with open('filters.json','r') as filters_file:
    filters = json.load(filters_file)
    keywords = filters["keywords"]
    locations = [loc.lower() for loc in filters["locations"]]

# Initialize the API.
api = TwitterAPI(creds['consumer_key'], creds['consumer_secret'],
                 creds['access_token'], creds['access_token_secret'])

# Access the stream.  Filter by keywords
stream = api.request('statuses/filter', {'track':",".join(keywords)})

### Create sqlite3 database
# con = sqlite3.connect('flags_stream.db')
# con.text_factory = str
# cur = con.cursor()

# Clear out the previous result files.
with open('flagged_tweets.txt','w') as output_file:
    output_file.write("")
with open('flagged_tweets_raw.txt','w') as output_file_raw:
    output_file_raw.write("")

# Consume streaming tweets
for tweet in stream.get_iterator():
    # Get location & possibly exact address
    user_location = tweet['user']['location']
    coordinates = tweet['coordinates']
    address = ""
    if coordinates:
        # Reverse Geocode
        try:
            lat = coordinates['coordinates'][1]
            lng = coordinates['coordinates'][0]
            url = ("https://maps.googleapis.com/maps/api/geocode" +
                   "/json?latlng=" + str(lat) + "," + str(lng) +
                   "&sensor=true")
            google_response = urllib.request.urlopen(url)
            geodata = json.loads(google_response.read().decode())
            address = geodata['results'][0]['formatted_address']
        except:
            print("Reverse Geocode Failed")
            traceback.print_exc()

    # Now filter by location
    #  -this if statement could def be better, but it works for now
    if any((" " + loc + " ") in (" " + address + " " + user_location + " ").
            lower() for loc in locations):
        print("Tweet Found:")
        info_output = ""

        # get rest of info
        name = tweet['user']['name']
        screen_name = tweet['user']['screen_name']
        followers = int(tweet['user']['followers_count'])
        tweet_text = tweet['text']

        # Lookup user's past tweets.  Sum up the times keywords are used in
        #  user's last 200 tweets. (200 is API limit per request)
        total_flags = 0
        try:
            r = api.request('statuses/user_timeline',
                            {'screen_name':screen_name,'count':'200'})
            for item in r.get_iterator():
                for phrase in keywords:
                    if all(word in item['text'].lower() for
                            word in phrase.lower().split()):
                        total_flags += 1
                        break # no need to test this tweet for other phrases
        except:
            print("REST Lookup of user failed")
            traceback.print_exc()

        # Now build the string output for this user's info
        info_output = ("Name: " + name + "\n" +
                       "Screen_Name: " + screen_name + "\n" +
                       "Location: " + user_location + "\n" +
                       "Coordinates: " + str(coordinates) + "\n" +
                       "Address: " + address + "\n" +
                       "Followers Count: " + str(followers) + "\n" +
                       "Flagged Tweet: " + tweet_text + "\n" +
                       "Total Flags: " + str(total_flags) + "\n\n")

        # Write output in text & raw json formats
        try:
            with open('flagged_tweets.txt','a') as output_file:
                output_file.write(info_output)
            with open('flagged_tweets_raw.txt','a') as output_file_raw:
                # To later load this a json object, this can be read back in as
                #  a string, enclosed in a of square brackets, and then loaded
                #  as a json object
                output_file_raw.write(json.dumps(tweet, indent=4) + ",\n")
        except:
            print("Writing to text file failed")
            traceback.print_exc()

        #    # Write output to database
        #         try:
        #             cur.executescript("""
        #             DROP TABLE IF EXISTS Tweets;
        #             CREATE TABLE Tweets(ID PRIMARY KEY NULL, Name TEXT, Screen_Name TEXT, Address TEXT, Latitude FLOAT, Longitude FLOAT, Tweet_Text TEXT, Word_Count INT, Followers INT);
        #             """)
        #             cur.execute("""INSERT INTO Tweets (Name, Screen_Name, Address, Latitude, Longitude, Tweet_Text, Word_Count, Followers) VALUES(?,?,?,?,?,?,?,?)""", (name, screen_name, address, lat, lng, tweet_text, word_count, followers))
        #             con.commit()
        #         except:
        #             print("Writing to db failed")


        # # Send a text message (using a carrier's email-to-SMS address)
        #     try:
        #         sender = 'Twitter Suicide Watch'
        #         receiver = phone + carrier
        #         message = """From: Twitter Suicide Watch
        #         \n
        #         \n
        #         Screen Name: """ + screen_name +"\n" + "Tweet: " + tweet_text + "\n"
        #         smtpObj = smtplib.SMTP(smtp_server, 25)
        #         smtpObj.starttls()
        #         smtpObj.login(email, password)
        #         smtpObj.sendmail(sender, receiver, message)
        #         smtpObj.quit()
        #         print("Successfully sent email")
        #     except:
        #         print("Couldn't send email")
        print(info_output)

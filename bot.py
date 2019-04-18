#!/usr/bin/env python3
#############################################################################
#    GaumutraBot v2
#    Copyright (C) 2019  Meribetisunnyleone
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.
#############################################################################
__author__ = 'Meribetisunnyleone'

import os
from os.path import isfile
from sys import argv, exit
from time import sleep
import signal
import pickle
import praw

SUBREDDIT = argv[1]                                 # the subreddit the bot lives on
INVOKE = '!redditgaumutra'                          # invocation
REPLY_SKELETON = open('skeleton.txt', 'r').read()   # skeleton of the reply
SCORE_FILE = "score.p"                              # where we store the score

# Login details
USERNAME = ''
PASSWORD = ''
CLIENTID = ''
CLIENTSECRET = ''
USERAGENT = ''

already_replied = []    # comments we've already replied to
score = {}              # keep track of number of times someone has gotten redditgaumutra

REDDIT_API = praw.Reddit(client_id=CLIENTID,
                         client_secret=CLIENTSECRET,
                         username=USERNAME,
                         password=PASSWORD,
                         user_agent=USERAGENT)

def make_reply(giver, getter, number):
    '''
    frame the reply
    '''
    reply = REPLY_SKELETON
    reply = reply.replace("GIVER", giver)
    reply = reply.replace("GETTER", getter)
    reply = reply.replace("NNNNN", number)
    reply = reply.replace("AUTHOR", "http://reddit.com/u/{}".format(__author__))
    return reply

def add_to_database(comment):
    '''
    add comment id to our database
    '''
    global already_replied
    already_replied.append(comment.id)
    #print("[*] Added {}: {} by {}".format(comment.id, comment.body, comment.author.name))

def init_database():
    '''
    load up or create a database
    '''
    global already_replied
    global score
    
    # Doing this is slower but also saves storage on the Pi.
    print("[*] Loading database...")
    r = REDDIT_API.redditor(USERNAME)
    for comment in r.comments.new(limit=None):
        add_to_database(comment.parent())
    
    print("[*] Loading score...")    
    if isfile(SCORE_FILE):
        if os.stat(SCORE_FILE).st_size != 0:
            score = pickle.load(open(SCORE_FILE, 'rb'))

    #print(score)
    print("[*] Database loaded")

def verify_comment(comment):
    '''
    verify if we need to reply to a comment
    '''
    global already_replied
    if INVOKE in comment.body:
        if comment.id not in already_replied:
            if not comment.archived:
                if comment.author != None:
                    if comment.parent().author != None:
                        if comment.parent().author != comment.author:
                            #print("VERIFIED: {} BY {} GIVEN TO {}".format(comment.body, comment.author.name, comment.parent().author.name))
                            return True
    return False

def fetch_score(name):
    '''
    returns (score for name)
    '''
    global score
    if not name in score:
        score[name] = 0
    return score[name]
    

def add_to_score(name):
    '''
    add 1 to score if name exists or initialize name in score with value 1
    '''
    global score
    if name not in score:
        score[name] = 1
    else: 
        score[name] += 1
    
def run_bot(sub):
    '''
    main
    '''
    subreddit = REDDIT_API.subreddit(sub)

    print("[*] Bot started")
    while True:
        for comment in subreddit.stream.comments():
            if verify_comment(comment):
                try:
                    giver = comment.author
                    getter = comment.parent().author
                    n = fetch_score(getter.name) + 1

                    reply = make_reply(giver=giver.name, getter=getter.name, number=str(n))
                    
                    comment.reply(reply)

                    add_to_score(getter.name)
                    add_to_database(comment)
                    
                    #print("[*] {} gave redditgaumutra to {}".format(comment.author.name, comment.parent().author.name))            
                except praw.exceptions.APIException as err:
                    # get the sleeptime from the error.
                    sleeptime = int(str(err).split(" ")[10]) + 2

                    print("[x] RATE LIMIT HIT: sleeping for {} minutes".format(sleeptime))
                    sleep(sleeptime*60)
                    
                    comment.reply(reply)
                    
                    add_to_score(getter.name)
                    add_to_database(comment)
                except Exception as err:
                    print(err)
                    clean_exit(0, 0) # reddit has some problems. 
                    

def clean_exit(what, ever):
    global score
    print("[*] Initiating shutdown")

    # pickle dump the score
    pickle.dump(score, open(SCORE_FILE, 'wb'))
    
    print("[*] Exit")
    exit(0)

if __name__=='__main__':
    signal.signal(signal.SIGINT, clean_exit)
    init_database()
    run_bot(SUBREDDIT)
    clean_exit(0, 1)

#!/usr/bin/python

"""
PiMessage utility functions to be used in both the daemon and the main
program

2014 Nate Fischer, Ivan De Dios

"""

import subprocess
import time
import datetime

TUPLE_FAIL = (None, None)

def getUser():
    username = subprocess.Popen('whoami', stdout=subprocess.PIPE).communicate()[0]
    username = username.rstrip('\n') # removes trailing newline
    return username

def nameFromIp(ip):
    # returns the name associated with the ip address
    # returns empty string on failure

    dataDir = "/home/"+getUser()+"/.pimessage/"
    name = ""
    with open(dataDir+"contacts") as fp:
        for line in fp:
            rec = line.split('\t')
            if rec[1].rstrip('\n') == ip:
                name = rec[0]
                break

    #print "You're contacting %s" % name
    return name


def saveMessage(msgString, mode):
    # This parses the message to save the appropriate message contents into the correct conversation file
    # This will create that conversation file if necessary
    # This returns a tuple containing the 'from' IP address and timestamp
    # Returns TUPLE_FAIL on failure

    lines = msgString.split('\n')

    # strip off the message's metadata
    othAddress = ""
    if mode == "rec":
        othAddress = lines[1]
    elif mode == "send":
        othAddress = lines[0]
    else:
        return TUPLE_FAIL

    timeStamp = int(float(lines[2]) ) # necessary to truncate
    msgData = lines[4:]

    # find out who wrote this file
    contact = nameFromIp(othAddress)
    dataDir = "/home/"+getUser()+"/.pimessage/"
    convFile = dataDir+"conversations/"+contact+".conv"

    if mode == "send":
        contact = "You"

    # write the newly received message to disc
    try:
        f = open(convFile, 'a')
        f.write(contact+" wrote:\n")
        for k in msgData:
            f.write(k+'\n')

        value = datetime.datetime.fromtimestamp(timeStamp)
        formattedStamp = value.strftime('%m/%d/%Y %H:%M')
        f.write(formattedStamp+'\n\n')

        f.close()
    except:
        # some sort of error, so let's return failure state
        return TUPLE_FAIL


    return (othAddress, timeStamp)

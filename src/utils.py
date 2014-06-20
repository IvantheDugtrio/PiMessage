#!/usr/bin/python

"""
PiMessage utility functions to be used in both the daemon and the main
program

2014 Nate Fischer, Ivan De Dios

"""

import time
import datetime

TUPLE_FAIL = (None, None)

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

    timeStamp = int(float(lines[2]) )
    msgData = lines[4:]

    # find out who wrote this file
    contact = "Nate"
    convFile = "sample.txt"

    # write the newly received message to disc
    try:
        f = open(convFile, 'w')
        f.write(contact+" wrote:\n")
        for k in msgData:
            f.write(k+'\n')

        value = datetime.datetime.fromtimestamp(timeStamp)
        formattedStamp = value.strftime('%m/%d/%Y %H:%M')
        f.write(formattedStamp)
        print(formattedStamp)

        f.close()
    except:
        # some sort of error, so let's return failure state
        return TUPLE_FAIL


    return (othAddress, timeStamp)

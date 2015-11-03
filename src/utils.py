#!/usr/bin/python

"""
PiMessage utility functions to be used in both the daemon and the main
program

2014 Nate Fischer, Ivan De Dios

"""

import os
import datetime

TUPLE_FAIL = (None, None)

def get_home_dir():
    """Return home directory"""
    return os.path.expanduser("~")

def ip_to_name(ip_addr):
    """
    returns the name associated with the ip_addr address
    returns empty string on failure
    """

    data_dir = os.path.join(get_home_dir(), ".pimessage/")
    name = ""
    with open(data_dir+"contacts") as fname:
        for line in fname:
            rec = line.split('\t')
            if rec[1].rstrip('\n') == ip_addr:
                name = rec[0]
                break

    #print "You're contacting %s" % name
    return name


def save_msg(msg_str, mode):
    """
    This parses the message to save the appropriate message contents into
    the correct conversation file
    This will create that conversation file if necessary
    This returns a tuple containing the 'from' IP address and timestamp
    @returns TUPLE_FAIL on failure
    """

    lines = msg_str.split('\n')

    # strip off the message's metadata
    oth_addr = ""
    if mode == "rec":
        oth_addr = lines[1]
    elif mode == "send":
        oth_addr = lines[0]
    else:
        return TUPLE_FAIL

    time_stamp = int(float(lines[2])) # necessary to truncate
    msg_data = lines[4:]

    # find out who wrote this file
    contact = ip_to_name(oth_addr)
    if contact == "":
        contact = oth_addr
    data_dir = os.path.join(get_home_dir(), ".pimessage/")
    conv_file = data_dir+"conversations/"+contact+".conv"
    if mode == "send":
        contact = "You"


    # write the newly received message to disc
    try:
        with open(conv_file, 'a') as fname:
            fname.write(contact+" wrote:\n")
            for k in msg_data:
                fname.write(k+'\n')

            value = datetime.datetime.fromtimestamp(time_stamp)
            formatted_stamp = value.strftime('%m/%d/%Y %H:%M')
            fname.write(formatted_stamp+'\n\n')
    except (TypeError, IOError):
        # some sort of error, so let's return failure state
        return TUPLE_FAIL


    return (oth_addr, time_stamp)

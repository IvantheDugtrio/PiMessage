#!/usr/bin/python

import subprocess
import re

IP_FAILURE = 1
PORT_NUM = 16246

def stringSlice(inString, searchString):
    # slices the input string so that the searchString is the beginning of
    # the returned string.  So if you pass in "hello world" as the first
    # string and then "lo" as the second string, this function will return
    # "lo world". If you pass in "foo" as the second string instead, you
    # will get "" returned. If you pass in "h" as the first string, you
    # will get "hello world" as the output.

    searchSub = inString.find(searchString)
    if searchSub == -1:
        returner = ""
    else:
        returner = inString[searchSub:]
    return returner

def getHostIp():
    # Returns the user's WLAN or LAN ip address if connected to a network
    # Returns IP_FAILURE if no address was found

    ipaddress = IP_FAILURE # default case
    cmdOutput = subprocess.Popen('ifconfig', stdout=subprocess.PIPE).communicate()[0]


    ## slice the cmdOutput string:
    modifiedOutput = stringSlice(cmdOutput, "wlan0")
    if modifiedOutput == "":
        modifiedOutput = stringSlice(cmdOutpt, "eth0")
        if modifiedOutput == "":
            return IP_FAILURE

    modifiedOutput = stringSlice(modifiedOutput, "inet")
    if modifiedOutput == "":
        return IP_FAILURE

    # slice the cmdOutput string:
    modifiedOutput = stringSlice(modifiedOutput, ":")
    if modifiedOutput == "":
        return IP_FAILURE

    ## perhaps there is a good way to clean this up? ##
    match_object = re.search('\d', modifiedOutput)
    if match_object: # it returned a match
        startSub = match_object.start()
    else:
        return IP_FAILURE

    match_object = re.search(' ', modifiedOutput)
    if match_object: # it returned a match
        endSub = match_object.start()
    else:
        return IP_FAILURE

    ipaddress = modifiedOutput[startSub:endSub]
    #ipcmd = "wget -qO- icanhazip.com"
    #ipaddress = subprocess.Popen(ipcmd.split(), stdout=subprocess.PIPE).communicate()[0]

    #ipaddress = ipaddress.rstrip()


    return ipaddress # default is IP_FAILURE

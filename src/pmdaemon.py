#!/usr/bin/python

import socket
import sys

import ip # local file
import utils
import datetime
import time
import os
import subprocess

"""
This is the PiMessage daemon. This acts as a server running on every user's
computer to receive PiMessages sent over LAN.

2014 Nate Fischer, Ivan De Dios

"""

ERR_FILE = os.path.join(utils.getHomeDir(), ".pimessage", "daemonError.log")
FLAG_FILE = os.path.join(utils.getHomeDir(), ".pimessage", "flag")

def errLog(msg):
    # log an error with its time followed by the message describing it

    now = datetime.datetime.now().time()
    formattedStamp = now.strftime('%H:%M %m/%d/%Y')
    errMsg = '\t'.join([formattedStamp, msg])
    #print >>sys.stderr, errMsg
    f = open(ERR_FILE, 'a')
    f.write(errMsg+'\n')
    f.close()

## Checks if the daemon is starting in detached mode
## If not, this will immediately terminate so that the user can still login
def checkStartup():
    # Wait 1 second for the program after this one to create a file
    time.sleep(0.5)

    # Now check for the file
    if os.path.isfile(FLAG_FILE):
        # Remove the flag file and continue
        os.remove(FLAG_FILE)
        return
    else:
        # This probably didn't start in daemon mode, so terminate
        errLog("Daemon likely did not start correctly. Consider uninstalling")
        exit(1)

## This creates the flag file if the -f option is supplied.
## This is NOT run in detached mode, so it must terminate IMMEDIATELY
def markFlag():
    if os.path.isfile(FLAG_FILE):
        errLog("pmdaemon did not close properly last time")
    f = open(FLAG_FILE, 'w')
    f.write("pimessage\n")
    f.close()
    exit(0)

if len(sys.argv) > 1:
    if sys.argv[1] == "-f":
        markFlag()
        exit(0) # just in case

checkStartup()

#errLog("Starting pmdaemon") # DEBUG

# fetch IP address of machine
serverIp = ip.getHostIp()
k = 0
while serverIp == ip.IP_FAILURE and k < 360:
    time.sleep(5)
    serverIp = ip.getHostIp()
    k = k + 1

if k >= 360:
    errLog("Error: PiMessage Daemon timed out. Unable to start. IP address could not be found")
    exit(1)

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server_address = (serverIp, ip.PORT_NUM)

try:
    sock.bind(server_address)
except:
    errLog("Error: Unable to start PiMessage Daemon. Perhaps it's already running?")
    exit(1)

# listen for incoming connections
sock.listen(1)

while True:
    # Wait for a connection
    connection, client_address = sock.accept()
    packets = []

    try:
        while True:
            data = connection.recv(16)
            packets.append(data)
            if data:
                connection.sendall(data)
            else:
                break

    finally:
        connection.close()

        message = "".join(packets) # concatenate all packets together

        lines = message.split('\n')

        # verify that this message is going to the correct IP
        if lines[0] == serverIp: # don't accept otherwise
            #print message

            ret = utils.saveMessage(message, "rec")
            if ret == utils.TUPLE_FAIL:
                # log the error
                errLog("There was an error saving your message.")

            # inform the user that they got a pimessage
            # todo



        # then return to receive more messages











exit(0)

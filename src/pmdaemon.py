#!/usr/bin/python

"""
This is the PiMessage daemon. This acts as a server running on every user's
computer to receive PiMessages sent over LAN.

2014 Nate Fischer, Ivan De Dios

"""

import socket
import sys

import ip # local file
import utils
import datetime
import time
import os

ERR_FILE = os.path.join(utils.get_home_dir(), '.pimessage', 'daemonError.log')
FLAG_FILE = os.path.join(utils.get_home_dir(), '.pimessage', 'flag')

def err_log(msg):
    """log an error with its time followed by the message describing it"""

    now = datetime.datetime.now().time()
    formatted_stamp = now.strftime('%H:%M %m/%d/%Y')
    err_msg = '\t'.join([formatted_stamp, msg])
    # print >>sys.stderr, err_msg
    with open(ERR_FILE, 'a') as fname:
        fname.write(err_msg+'\n')

def check_startup():
    """
    Checks if the daemon is starting in detached mode
    If not, this will immediately terminate so that the user can still login
    """

    # Wait 1 second for the program after this one to create a file
    time.sleep(0.5)

    # Now check for the file
    if os.path.isfile(FLAG_FILE):
        # Remove the flag file and continue
        os.remove(FLAG_FILE)
        return
    else:
        # This probably didn't start in daemon mode, so terminate
        err_log('Daemon likely did not start correctly. Consider uninstalling')
        exit(1)

def mark_flag():
    """
    This creates the flag file if the -f option is supplied.
    This is NOT run in detached mode, so it must terminate IMMEDIATELY
    """
    if os.path.isfile(FLAG_FILE):
        err_log('pmdaemon did not close properly last time')
    with open(FLAG_FILE, 'w') as fname:
        fname.write('pimessage\n')
    exit(0)

if len(sys.argv) > 1:
    if sys.argv[1] == '-f':
        mark_flag()
        exit(0) # just in case

check_startup()

# err_log('Starting pmdaemon') # DEBUG

# fetch IP address of machine
SERVER_IP = ip.get_host_ip()
k = 0
while SERVER_IP == ip.IP_FAILURE and k < 360:
    time.sleep(5)
    SERVER_IP = ip.get_host_ip()
    k = k + 1

if k >= 360:
    err_log('Error: PiMessage Daemon timed out. Unable to start. IP address '
            'could not be found')
    exit(1)

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

SERVER_ADDRESS = (SERVER_IP, ip.PORT_NUM)

try:
    sock.bind(SERVER_ADDRESS)
except socket.error:
    err_log('Error: Unable to start PiMessage Daemon. '
            "Perhaps it's already running?")
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

        MESSAGE = ''.join(packets) # concatenate all packets together

        lines = MESSAGE.split('\n')

        # verify that this MESSAGE is going to the correct IP
        if lines[0] == SERVER_IP: # don't accept otherwise
            #print MESSAGE

            RET = utils.save_msg(MESSAGE, 'rec')
            if RET == utils.TUPLE_FAIL:
                # log the error
                err_log('There was an error saving your message.')

            # inform the user that they got a pimessage
            # todo

exit(0)

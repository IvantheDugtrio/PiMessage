#!/usr/bin/python

import socket
import sys

import ip # local file
import utils

"""
This is the PiMessage daemon. This acts as a server running on every user's
computer to receive PiMessages sent over LAN.

2014 Nate Fischer, Ivan De Dios

"""

#print >>sys.stdout, "Starting pmdaemon" # DEBUG

# fetch IP address of machine
serverIp = ip.getHostIp()
if serverIp == ip.IP_FAILURE:
    print >>sys.stderr, "Error: Unable to start PiMessage Daemon."
    print >>sys.stderr, "IP address could not be found"
    exit(1)

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server_address = (serverIp, ip.PORT_NUM)

try:
    sock.bind(server_address)
except:
    print "Error: Unable to start PiMessage Daemon."
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

            utils.saveMessage(message, "rec")

            # inform the user that they got a pimessage



        # then return to receive more messages











exit(0)

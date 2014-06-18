#!/usr/bin/python

import socket
import sys

import ip # local file

# fetch IP address of machine
serverIp = ip.getHostIp()
if serverIp == ip.IP_FAILURE:
    print >>sys.stderr, "Error: Unable to start PiMessage Daemon."
    print >>sys.stderr, "IP address could not be found"
    exit(1)

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server_address = (serverIp, 10000)

sock.bind(server_address)

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
        print message

        # verify that this message is going to the correct IP

        # identify who this message is from & sort accordingly

        # strip off the message's metadata

        # write the newly received message to disc

        # inform the user that they got a pimessage



        # then return to receive more messages











exit(0)

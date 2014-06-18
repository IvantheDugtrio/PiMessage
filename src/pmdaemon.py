#!/usr/bin/python

import socket
import sys

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server_address = ('192.168.1.10', 10000)

sock.bind(server_address)

# listen for incoming connections
sock.listen(1)
print "done listening"

while True:
    # Wait for a connection
    print "done waiting"
    connection, client_address = sock.accept()

    try:
        while True:
            data = connection.recv(16)
            print 'received "%s"' % data
            if data:
                connection.sendall(data)
            else:
                break

    finally:
        connection.close()

        # right here is where I need to handle writing the data to file or closing the file for the conversation

        # inform the user that they got a pimessage











exit(0)

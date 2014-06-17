#!/usr/bin/python

import socket
import sys

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server_address = ('localhost', 10000)

sock.bind(server_address)

# listen for incoming connections
sock.listen(1)
print "done listening"

while True:
    # Wait for a connection
    connection, client_address = sock.accept()
    print "done waiting"

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











exit(0)

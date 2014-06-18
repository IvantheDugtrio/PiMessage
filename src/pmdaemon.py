#!/usr/bin/python

import socket
import sys

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server_address = ('192.168.1.10', 10000)

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

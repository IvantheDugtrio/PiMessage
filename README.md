PiMessage
=========

This is a lightweight Python-based peer to peer LAN messenger. Users on each Linux device can send
each
other IM messages. If the user is on a raspberry pi, then sending over GPIO
pins is also an option.

Functionality
---------
Some project features will include:

1. Sending messages over internet
2. Handshake authentication system, allowing users to connect to each other securely and knowingly
3. Versatile user interface (CLI and possibly GUI)
4. Sending a "so-and-so is writing something" message, similar to some other messaging systems
5. Messaging over GPIO pins for the Raspberry Pi

Development
---------
This project is currently fairly usable as a LAN messenger. Messaging,
storing contacts, saving messages, installing/uninstalling, and many other
features are mostly bug-free.

The most obvious features that still need to be developed, however, are as
follows:
- No notification of when you get a new message
- GPIO messaging is still unavailable
- The daemon doesn't always run properly on start up
- Cannot send a message to someone without first adding them as a contact

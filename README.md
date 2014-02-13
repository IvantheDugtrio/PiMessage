-PiMessage README (2/13/14)

-

-This is a peer to peer messenger program which connects two or more Raspberry 

-Pis over the internet. Users on each Pi can send each other messages in text or

-even in GPIO commands (if the recepient allows this).

-

-The development will be broken up as follows:

-1. Networking code for sending data across the internet (to be figured out)

-2. Handshake authentication system using hashed keys which fit an algorithm. 

-   This will allow users to connect to each other securely and knowingly

-3. User interface (GUI and/or terminal). Can be done with Qt for ease of GUI design.

-4. Text messaging system (with strings presumably)

-5. GPIO messaging (using Python commands that get interpreted on the recepient's pi.

-

-That is all for now.

#!/usr/bin/python

"""
A messaging program between two Linux systems, optimized for the raspberry
pi running raspbian OS.

2014 Nate Fischer, Ivan De Dios

"""

import subprocess   # for function calls
import os
import sys          # for arg parsing
import string
import re           # for searching
import time
import datetime
import mmap
import socket       # for networking

import ip           # local file
import utils

## make sure indents are 4 spaces if possible
## vim settings:
##              set et
##              set ts=4

## perhaps an IPaddress class? This would mean changing some variable names


########################
##  Global constants  ##
########################

IP_FAILURE = ip.IP_FAILURE
DIR_FAILURE = 2
NULL_ARGUMENT = ""

########################
##  Global variables  ##
########################

# values are listed here, but should not be uncommented
global hostIp
global operatingSystem

########################
##  Helper functions  ##
########################

def mdUnix(name):
    if os.system("mkdir " + name) != 0:
        return DIR_FAILURE
    else:
        return 0

def initNewUser(user, homedir):
    print "Initializing new user"

    # Let's make sure everyone knows for sure that this is being installed
    installMessage = """
    Do you grant piMessage permission to install on your computer?

    PiMessage will have access to:

    - your IP address
    - any contacts you enter into PiMessage
    - all of your conversations through PiMessage

    PiMessage will create on your computer:

    - a directory to save the following PiMessage information
    - a file to save your contacts and their saved IP addresses
    - your conversations with contacts
    - your preferred text editor

    """
    print installMessage
    decision = raw_input("Do you want to install PiMessage? (y/n): ")
    if decision != "y":
        print "Not installing. Terminating PiMessage."
        exit(1)

    # make the directory
    if os.system("test -d " + homedir) != 0:
        if mdUnix(homedir) == DIR_FAILURE:
            exit(DIR_FAILURE)

    # generate user's keys
    # todo


    # Get user input
    # write info to files
    open(homedir+"editor", 'w').write("vim") # doesn't terminate in newline

    if os.system("test -d " + homedir + "conversations") != 0:
        if mdUnix(homedir + "conversations") == DIR_FAILURE:
            exit(DIR_FAILURE)
        else:
            # create permissions
            os.system("chmod 700 " + homedir + "conversations")


    open(homedir+"contacts", 'w').write("") # doesn't terminate in newline

    print "PiMessage has been successfully installed."


    exit(0)

def grabOpt(argv, n):
    # returns the nth arg or returns NULL_ARGUMENT
    if len(argv) <= n:
        return NULL_ARGUMENT
    else:
        return argv[n]

def parseOpts(argv, editCmd):
    scriptName = argv[0]
    secOpt = grabOpt(argv, 2)
    primOpt = grabOpt(argv, 1)

    if primOpt == NULL_ARGUMENT:
        # only contains the script name, no arguments
        # call usage function
        usage(scriptName)
        exit(1)


    if primOpt == "-h" or primOpt == "--help" or primOpt == "help":
        usage(scriptName)
        exit(0)
    elif primOpt == "ip": # show host IP address
        print hostIp # a global value

    elif primOpt == "history" or primOpt == "recent":
        # show recent chat history
        val = ""
        if secOpt == "-a":
            val = showRecents(True)
        else:
            val = showRecents(False)
        exit(val)
    elif primOpt == "new" or primOpt == "compose": # compose a message
        if secOpt == NULL_ARGUMENT:
            print "Invalid number of operands for %s option" % primOpt
            usage(scriptName)
            exit(1)
        
        thirdOpt = grabOpt(argv, 3)
        fourthOpt = grabOpt(argv, 4)

        if thirdOpt == "-m" and fourthOpt != NULL_ARGUMENT:
            sendMessage(secOpt, editCmd, fourthOpt)
        else:
            sendMessage(secOpt, editCmd)

    elif primOpt == "read": # read a conversation
        if secOpt == NULL_ARGUMENT:
            print "Invalid number of operands for %s option" % primOpt
            usage(scriptName)
            exit(1)
        val = readConvo(secOpt)
        exit(val)

    elif primOpt == "rm-convo": # delete a conversation
        if secOpt == NULL_ARGUMENT:
            print "Invalid number of operands for %s option" % primOpt
            usage(scriptName)
            exit(1)

        val = rmConvo(secOpt)
        exit(val)

    elif primOpt == "resend": # resend a failed message
        if secOpt == NULL_ARGUMENT:
            print "Invalid number of operands for %s option" % primOpt
            usage(scriptName)
            exit(1)

        print "second option is", secOpt
        print("Under construction.")
        exit(3)


    elif primOpt == "contacts":
        # contacts of the form:
        # Adam Smith\t1.2.3.4
        # Betty Rogers\t98.76.54.321

        # Display the contact list in less
        if secOpt == "-a":
            # show IP addresses in output
            os.system("less "+dataDir+"contacts")
        else:
            # remove IP addresses from output
            os.system("sed 's/\t.*$//' " + dataDir+"contacts | less")

        exit(0)


    elif primOpt == "add":
        thirdOpt = grabOpt(argv, 3)

        if thirdOpt == NULL_ARGUMENT:
            print "Invalid number of operands for %s option" % primOpt
            usage(scriptName)
            exit(1)

        # default is to NOT overwrite (prompt user if they want to change)
        addContact(secOpt, thirdOpt, "n")


    elif primOpt == "force-link":
        # force-link a contact to an IP
        # essentially, just overwrite a contact's IP

        thirdOpt = grabOpt(argv, 3)

        if thirdOpt == NULL_ARGUMENT:
            print "Invalid number of operands for %s option" % primOpt
            usage(scriptName)
            exit(1)

        # default is to overwrite old contact
        addContact(secOpt, thirdOpt, "y")


    elif primOpt == "rm-contact":
        if secOpt == NULL_ARGUMENT:
            print "Invalid number of operands for %s option" % primOpt
            usage(scriptName)
            exit(1)

        ret = rmContact(secOpt)
        if ret != 0:
            print "Error in removing your contact."
            exit(ret)

        resp = raw_input("Would you also like to delete conversation history for this contact? (y/n) ")
        if resp == "y" or resp == "yes" or resp == "Y":
            print "deleting conversation for", secOpt
            ret = rmConvo(secOpt)

        exit(ret)

    else:
        # some invalid option
        print "Invalid option %s" % primOpt
        usage(scriptName)
        exit(1)



########################
##  Option functions  ##
########################

def usage(scriptName):
    # Prints usage/help information
    # This is called by --help, -h, or invalid usage

    # print usage info
    print "Usage: %s [options] [option arguments]\n" % scriptName

    # print help/option info
    # Don't indent on docstring
    optionMsg = """Options:
help, -h, --help                           help
ip                                         show host IP address
history, recent        [-a]                show recent chat history
compose, new           CONTACT [-m "msg"]  compose & send message
read                   CONTACT             read a conversation
rm-convo               CONTACT             delete a conversation
resend                 CONTACT             resend a failed message
force-link             CONTACT, IP         force-link contact to IP
config                 VARIABLE, VALUE     configure varialbles
contacts               [-a]                view contact list [with IPs]
add                    CONTACT, IP         add a contact
rm-contact             CONTACT             delete a contact

"""

#-i , --show-ip                   Show your IP address
#-s , --history                   Show your recent chat history
#-c , --compose     CONTACT       Compose & send message
#-r , --read        CONTACT       Read a conversation
#-d , --delete      CONTACT       Delete a conversation
#-q , --resend      CONTACT       Resend a failed message
#-h , --help                      Help
#-f , --force-link  CONTACT, IP   Specify the IP address to try for CONTACT
#
#    """

    print(optionMsg)

    return # exit after calling this function


def addContact(name, ip, overwrite):
    # Search for if this person is already there
    myFile = open(dataDir+"contacts", "r")
    allContacts = myFile.read()
    myFile.close()
    contactIndex = allContacts.find(name+"\t")
    if contactIndex != -1:
        if overwrite != "y":
            print "%s is already entered in your contact list." % name
            overwrite = raw_input("Would you like to overwrite this entry? (y/n) ")
        if overwrite != "y":
            print "Not overwriting the entry. Terminating."
            exit(1)
        else:
            # remove the old one
            rmContact(name)
            print "Your contact has been updated."


    # add contact normally
    myFile = open(dataDir+"contacts", "a")
    addString = name+"\t"+ip+"\n"
    myFile.write(addString)
    myFile.close()

    # use GNU sort
    sortCmd = "sort -f "+dataDir+"contacts > "+dataDir+"sort_contacts"
    os.system(sortCmd)

    # overwrite old file
    os.system("mv "+dataDir+"sort_contacts "+dataDir+"contacts")

    return 0

def rmContact(name):
    myFile = open(dataDir+"contacts", "r")
    allContacts = myFile.read()
    myFile.close()

    # this is the part up until that contact
    contactIndex = allContacts.find(name+"\t")
    if contactIndex == -1:
        # contact isn't in here
        return 1

    firstHalf = allContacts[0:contactIndex]

    # this is the part right after that contact until the end
    secondHalf = ip.stringSlice(allContacts, name)
    secondHalf = ip.stringSlice(secondHalf, '\n')
    secondHalf = secondHalf[1:]
    allContacts = firstHalf + secondHalf

    myFile = open(dataDir+"contacts", "w")
    myFile.write(allContacts) # add the new entry later
    myFile.close()

    return 0



#    # Raspberry Pi logo
#    print(string.center("   .~~.   .~~.   ", width))
#    print(string.center("  '. \ ' ' / .'  ", width))
#    print(string.center("   .~ .~~~..~.   ", width))
#    print(string.center("  : .~.'~'.~. :  ", width))
#    print(string.center(" ~ (   ) (   ) ~ ", width))
#    print(string.center("( : '~'.~.'~' : )", width))
#    print(string.center(" ~ .~ (   ) ~. ~ ", width))
#    print(string.center("  (  : '~' :  )  ", width))
#    print(string.center("   '~ .~~~. ~'   ", width))
#    print(string.center("       '~'       ", width))
#    print("")
#
#    raw_input("Press enter to continue... ")
#    return 0



def showRecents(isAll):
    # This shows the 10 most recent conversations & the top message in each
    # one by default. This has the option to show all recent conversations
    # in a similar fashion if `isAll' is True.

    # Build the list of recent conversations
    getConvoCmd = "ls -t "+dataDir+"conversations/"
    sortedConvos = subprocess.Popen(getConvoCmd.split(), stdout=subprocess.PIPE).communicate()[0]

    convoList = sortedConvos.split('\n')

    if not isAll:
        convoList = convoList[0:9]

    for k in convoList:
        # remove .conv from each conversation
        vals = k.split('.')
        if len(vals) == 2:
            k = vals[0]
        else:
            k = ".".join(vals[0:len(vals)-1] )

        print k

    return

def readConvo(myContact):
    # Read the saved conversation with this contact if one exists
    # Display a message to indicate if no conversation exists

    convFile = dataDir+"conversations/"+myContact+".conv"

    try:
        # If file can't be read, than we should return immediately
        f = open(convFile, 'r')
        f.close()
    except:
        print "It appears that you don't currently have a conversation with", myContact
        return 0

    return os.system("less "+convFile)

def rmConvo(myContact):
    # Delete the conversation for this contact
    # Display a message to indicate if no conversation exists

    convFile = dataDir+"conversations/"+myContact+".conv"

    try:
        # If file can't be read, than we should return immediately
        f = open(convFile, 'r')
        f.close()
    except:
        print "No conversation for", myContact, "could be found."
        return 1

    return os.system("rm "+convFile)

def sendMessage(myContact, editor, text=""):
    # fetch sender IP
    if hostIp == IP_FAILURE:
        exit(1)

    # fetch recipient IP

    recIp = ""
    with open(dataDir+"contacts") as fp:
        for line in fp:
            rec = line.split('\t')
            if rec[0] == myContact:
                recIp = rec[1].rstrip('\n')
                break

    ## Compose the message

    # store this in conversations directory
    fileName = dataDir+"conversations/msg"+myContact

    if text == "":
        ret = os.system(editor+" "+fileName)
        if ret != 0:
            print "Error in opening message file."
            exit(2)
    else:
        # use the short message typed by the user at the prompt
        try:
            f = open(fileName, 'w')
            f.write(text)
            f.close()
        except:
            print "Error composing your file on disc."
            exit(1)


    # prompt if they want to send or not
    shouldSend = raw_input("To send or not to send; that is the question (y/n): ")

    ss = shouldSend
    if ss != "y" and ss != "Y" and ss != "yes" and ss != "Yes" and ss != "YES":
        print "Your message has been saved for next time you compose a message to %s" % myContact
        exit(5)
    #if shouldSend != "eat me":
    #    exit(5)
    #elif shouldSend != "y":
    #    exit(5)
    #elif shouldSend != "yes":
    #    exit(5)
    #elif shouldSend != "Yes":
    #    exit(5)
    #elif shouldSend != "YES":
    #    exit(5)

    # get time stamp in proper format
    sendTime = str(time.time())

    # format the message with the meta data
    msgLines = []

    msgLines.append(recIp)
    msgLines.append(hostIp)
    msgLines.append(sendTime) # guaranteed two consecutive newlines
    msgLines.append("")

    with open(fileName) as fp:
        for line in fp:
           msgLines.append(line.rstrip('\n') )
    msgLines.append("")

    msgString = "\n".join(msgLines)

    # Send the full message

    s = socket.socket()
    host = socket.gethostname()
    port = 10000
    s.connect((recIp, port))

    try:
        s.sendall(msgString)

        amount_received = 0
        amount_expected = len(msgString)
        packets = []

        while amount_received < amount_expected:
            data = s.recv(16)
            amount_received += len(data)
            packets.append(data)

    finally:
        s.close()   # Close the socket when done
        recvMsg = "".join(packets)

        if msgString != recvMsg:
            print "There may be an error with the data sent"

    # add the message to conversation history
    ret = utils.saveMessage(msgString, "send")
    if ret == utils.TUPLE_FAIL:
        print "failure in saving your message."



    # clean up by removing old message to contact
    ret = os.system("rm "+fileName)
    if ret != 0:
        print "Error in removing message file."
        exit(2)


    return 0

########################
##   Main function    ##
########################

def main(argv):

    ## Get user information ##
    global operatingSystem
    operatingSystem = os.name
    if operatingSystem != "nt":
        operatingSystem = subprocess.Popen(['uname', '-s'], stdout=subprocess.PIPE).communicate()[0]
        operatingSystem = operatingSystem.rstrip('\n')
        # change Cygwin to say 'CYGWIN' always
        underScoreIndex = operatingSystem.find("_")
        if underScoreIndex != -1:
            operatingSystem = operatingSystem[:underScoreIndex]

    if operatingSystem != "Linux" and operatingSystem != "Darwin" and operatingSystem != "CYGWIN":
        print "Error: %s is not a supported operating system at this time." % operatingSystem
        exit(5)

    username = utils.getUser()

    global dataDir
    dataDir = "/home/" + username + "/.pimessage/"
    dirExistsCommand = "test -d " + dataDir
    if os.system(dirExistsCommand) != 0:
        initNewUser(username, dataDir)

    dirFiles = subprocess.Popen(['ls', '-A', dataDir], stdout=subprocess.PIPE).communicate()[0]

    # must be in correct ls -A order
    CORRECT_DIR_FILES = """contacts
conversations
editor
"""

    if dirFiles != CORRECT_DIR_FILES:
        initNewUser(username, dataDir)

    # get user's chosen editor
    editCommand = open(dataDir+"editor", 'r').read().rstrip('\n')
    if subprocess.Popen(['which', editCommand], stdout=subprocess.PIPE).communicate()[0] == "":
        print "Error: %s is not a valid editor. Please adjust your editor value" % editCommand
        exit(2)

    global hostIp
    hostIp = ip.getHostIp()
    if hostIp == IP_FAILURE:
        print "Error: your IP address could not be correctly retrieved."
        exit(2)

    # get number of rows and number of columns on terminal
    #screenRows, screenColumns = os.popen('stty size', 'r').read().split()
    #screenRows = int(screenRows)
    #screenColumns = int(screenColumns)


    ## User must already have information entered

    #keyPress = welcomeScreen(hostIp, screenColumns)



    ## Option parsing ##
    # figure out which option was called
    parseOpts(argv, editCommand)









    return 0



if __name__ == "__main__":
    status = main(sys.argv)
    exit(status)

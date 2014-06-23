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

def install(scriptName, user, homedir):
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


    if os.system("which vim >/dev/null 2>&1") == 0:
        myEdit = "vim"
    else:
        myEdit = "nano"

    for k in [0, 1, 2, 3]:
        if k == 3:
            print "Error: too many tries for editor."
            exit(1)
        # Get user input
        resp = raw_input("What is your preferred text editor? Press enter to default to "+myEdit+", enter 'cancel' to cancel the installation. ")
        if resp == "cancel" or resp == "'cancel'":
            # cancel the installation now
            exit(1)
        elif resp == "":
            print "Selecting", myEdit
            break
        else:
            # check if their editor is a valid command
            val = os.system("which "+resp+" >/dev/null 2>&1")
            if val == 0:
                myEdit = resp
                break
            else:
                print resp, "is not a recognized command."

    # write info to files
    f = open(homedir+"editor", 'w')
    f.write(myEdit) # doesn't terminate in newline
    f.close()

    if os.system("test -d " + homedir + "conversations") != 0:
        if mdUnix(homedir + "conversations") == DIR_FAILURE:
            exit(DIR_FAILURE)
        else:
            # create permissions
            os.system("chmod 700 " + homedir + "conversations")


    f = open(homedir+"contacts", 'w')
    f.write("") # doesn't terminate in newline
    f.close()
    dirPath = os.path.abspath(os.path.dirname(sys.argv[0]) )
    scriptName = dirPath+"/pimessage.py"

    # alias `pimessage' to point to this script
    grepAlias = ["grep", "^alias \+pimessage="+scriptName, "/home/"+user+"/.bashrc"]
    grepResults = subprocess.Popen(grepAlias, stdout=subprocess.PIPE).communicate()[0]
    if grepResults == "":
        # must append alias command
        try:
            f = open("/home/"+user+"/.bashrc", 'a')
            f.write("\n# For PiMessage -- do not delete\n")
            f.write("alias pimessage="+scriptName+"\n")
            f.close()
        except:
            print "Error applying shell alias for pimessage"

    # start pmdaemon at startup
    grepDaemon = ["grep", "^"+dirPath+"/pmdaemon.py", "/home/"+user+"/.profile"]
    grepResults = subprocess.Popen(grepDaemon, stdout=subprocess.PIPE).communicate()[0]
    if grepResults == "":
        # must append alias command
        try:
            f = open("/home/"+user+"/.profile", 'a')
            f.write("\n#start pimessage daemon\n")
            f.write(dirPath+"/pmdaemon.py &\n")
            f.close()
        except:
            print "Error loading PiMessage daemon in .profile"

        # start the daemon manually this time
        os.system(dirPath+"/pmdaemon.py &")




    print "PiMessage has been successfully installed."
    exit(0)


def uninstall():
    status = os.system('rm -r -f '+dataDir)
    if status != 0:
        print "Error removing PiMessage."
        print "Remove by deleting", dataDir
    else:
        print "PiMessage has been successfully uninstalled."
    return status


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
    elif primOpt == "logo":
        # This is a secret option to display the Raspberry Pi ASCII logo
        showLogo()
        exit(0)
    elif primOpt == "kill":
        # This is a secret option to kill the daemon
        status = killDaemon()
        exit(status)
    elif primOpt == "uninstall":
        # This is a secret option to completely remove PiMessage
        status = uninstall()
        exit(status)

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

        sendMessage(secOpt, editCmd, "", False)


    elif primOpt == "contacts":
        # contacts of the form:
        # Adam Smith\t1.2.3.4
        # Betty Rogers\t98.76.54.321
        s = secOpt
        t = grabOpt(argv, 3)

        # Display the contact list in less
        if (s == "-a" and t == "-o") or (s == "-o" and t == "-a"):
            # stdout, show IP addresses
            os.system("cat "+dataDir+"contacts")
        elif s == "-a" and t != "-o":
            # display in less, show IP addresses
            os.system("less "+dataDir+"contacts")
        elif s == "-o" and t != "-o":
            # stdout, no IP addresses
            os.system("sed 's/\t.*$//' " + dataDir+"contacts")
        else:
            # display in less, no IP addresses
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

    elif primOpt == "config":
        thirdOpt = grabOpt(argv, 3)
        if thirdOpt == NULL_ARGUMENT:
            print "Invalid number of operands for %s option" % primOpt
            usage(scriptName)
            exit(1)

        if secOpt == "editor":
            if os.system("which "+thirdOpt+" >/dev/null 2>&1") == 0:
                with open(dataDir+"editor", 'w') as f:
                    f.write(thirdOpt)
            else:
                print "Error: %s is not a recognized command." % thirdOpt

        else:
            print "Unknown variable. Cannot config."
            exit(1)

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
config                 VARIABLE, VALUE     configure variables
contacts               [-a, -o]            view contact list [with IPs]
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


def showLogo():
    msg = """
                                   PiMessage
                                   ---------

                                  .~~.   .~~.
                                 '. \ ' ' / .'
                                  .~ .~~~..~.
                                 : .~.'~'.~. :
                                ~ (   ) (   ) ~
                               ( : '~'.~.'~' : )
                                ~ .~ (   ) ~. ~
                                 (  : '~' :  )
                                  '~ .~~~. ~'
                                      '~'

"""
    print msg
    return

def killDaemon():
    # This will kill the PiMessage daemon
    # Note: this is NOT recommended for normal use

    dirPath = os.path.dirname(sys.argv[0])
    runScript = dirPath + "/killDaemon"
    return os.system(runScript)



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

def sendMessage(myContact, editor, text="", shouldCompose=True):
    # fetch sender IP
    #if hostIp == IP_FAILURE:
    #    exit(1)

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

    if shouldCompose:
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
    else:
        # check to see if a saved message actually exists
        try:
            f = open(fileName, 'r')
            f.close()
        except:
            # if we couldn't open the file, then we can't resend it
            print "Unable to find a saved message for", myContact
            exit(1)


    # prompt if they want to send or not
    #shouldSend = raw_input("To send or not to send; that is the question (y/n): ")

    #ss = shouldSend
    #if ss != "y" and ss != "Y" and ss != "yes" and ss != "Yes" and ss != "YES":
    #    print "Your message has been saved for next time you compose a message to %s" % myContact
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

    if hostIp != IP_FAILURE:
        s = socket.socket()
        host = socket.gethostname()
        port = ip.PORT_NUM
        try:
            s.connect((recIp, port))
        except:
            print "Error: Unable to send message. Perhaps you have an incorrect IP address?"
            exit(4)

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
    else:
        print "Please connect to a network to send your message."


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

    if operatingSystem != "Linux" and operatingSystem != "Darwin": # and operatingSystem != "CYGWIN":
        print "Error: %s is not a supported operating system at this time." % operatingSystem
        exit(5)

    username = utils.getUser()

    global dataDir
    dataDir = "/home/" + username + "/.pimessage/"

    firstOpt = grabOpt(argv, 1)
    if firstOpt == "uninstall":
        exit(uninstall() )


    scriptName = argv[0]
    dirExistsCommand = "test -d " + dataDir
    if os.system(dirExistsCommand) != 0:
        install(scriptName, username, dataDir)

    dirFiles = subprocess.Popen(['ls', '-A', dataDir], stdout=subprocess.PIPE).communicate()[0]

    # must be in correct ls -A order
    CORRECT_DIR_FILES = """contacts
conversations
editor
"""

    if dirFiles != CORRECT_DIR_FILES:
        install(scriptName, username, dataDir)

    # get user's chosen editor
    editCommand = open(dataDir+"editor", 'r').read().rstrip('\n')
    if subprocess.Popen(['which', editCommand], stdout=subprocess.PIPE).communicate()[0] == "":
        print "Error: %s is not a valid editor. Please adjust your editor value" % editCommand
        exit(2)

    global hostIp
    hostIp = ip.getHostIp()
    #if hostIp == IP_FAILURE:
    #    print "Error: your IP address could not be correctly retrieved."
    #    exit(2)


    ## User must already have information entered


    ## Option parsing ##
    # figure out which option was called
    parseOpts(argv, editCommand)









    return 0



if __name__ == "__main__":
    status = main(sys.argv)
    exit(status)

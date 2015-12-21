#!/usr/bin/python

"""
A messaging program between two Linux systems, optimized for the raspberry
pi running raspbian OS.

2014 Nate Fischer, Ivan De Dios

"""

import subprocess   # for function calls
import os
import sys          # for arg parsing
import shutil
import time
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
NULL_ARGUMENT = ''

########################
##  Global variables  ##
########################

# values are listed here, but should not be uncommented
global host_ip
global op_system

########################
##  Helper functions  ##
########################

def unix_mkdir(name):
    """Makes a directory on a unix system"""
    if os.system('mkdir ' + name) != 0:
        return DIR_FAILURE
    else:
        return 0

def install(script_name, homedir):
    """Installs the project"""
    print 'Initializing new user'

    # Let's make sure everyone knows for sure that this is being installed
    print """
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

    decision = raw_input('Do you want to install PiMessage? (y/n): ')
    if decision != 'y':
        print 'Not installing. Terminating PiMessage.'
        exit(1)

    # make the directory
    if os.system('test -d ' + homedir) != 0:
        if unix_mkdir(homedir) == DIR_FAILURE:
            exit(DIR_FAILURE)

    # generate user's keys
    # todo


    if os.system('which vim >/dev/null 2>&1') == 0:
        my_editor = 'vim'
    else:
        my_editor = 'nano'

    os.system('clear')
    for k in [0, 1, 2, 3]:
        if k == 3:
            print 'Error: too many tries for editor.'
            exit(1)
        # Get user input
        prompt = '\nWhat is your preferred text editor? Press enter to '
        prompt += 'default to '+my_editor+", enter 'cancel' to cancel the "
        prompt += 'installation. '
        resp = raw_input(prompt)
        if resp == 'cancel' or resp == "'cancel'":
            # cancel the installation now
            exit(1)
        elif not resp:
            print 'Selecting', my_editor
            break
        else:
            # check if their editor is a valid command
            if os.system('which '+resp+' >/dev/null 2>&1') == 0:
                my_editor = resp
                break
            else:
                print resp, 'is not a recognized command.'

    # write info to files
    with open(homedir+'editor', 'w') as fname:
        fname.write(my_editor) # doesn't terminate in newline

    if os.system('test -d ' + homedir + 'conversations') != 0:
        if unix_mkdir(homedir + 'conversations') == DIR_FAILURE:
            exit(DIR_FAILURE)
        else:
            # create permissions
            os.system('chmod 700 ' + homedir + 'conversations')


    with open(homedir+'contacts', 'w') as fname:
        fname.write('') # doesn't terminate in newline

    dir_path = os.path.abspath(os.path.dirname(sys.argv[0]))
    script_name = dir_path+'/pimessage.py'

    # alias `pimessage' to point to this script
    _bashrc = os.path.join(utils.get_home_dir(), '.bashrc')

    grep_results = subprocess.Popen(['grep', '^alias \\+pimessage='+script_name,
                                     _bashrc],
                                    stdout=subprocess.PIPE).communicate()[0]
    if grep_results == '':
        # must append alias command
        try:
            with open(_bashrc, 'a') as fname:
                fname.write('\n# For PiMessage -- do not delete\n')
                fname.write('alias pimessage='+script_name+'\n')
        except IOError:
            print 'Error applying shell alias for pimessage'

    # start pmdaemon at startup
    _profile = os.path.join(utils.get_home_dir(), '.profile')
    grep_daemon_cmd = ['grep', '^'+dir_path+'/pmdaemon.py', _profile]
    grep_results = subprocess.Popen(grep_daemon_cmd,
                                    stdout=subprocess.PIPE).communicate()[0]
    if not grep_results:
        # must append alias command
        start_daemon_cmd = dir_path+'/pmdaemon.py &'
        flag_cmd = dir_path+'/pmdaemon.py -f'
        try:
            with open(_profile, 'a') as fname:
                fname.write('\n'.join(['#start pimessage daemon',
                                       start_daemon_cmd, flag_cmd, '']))
        except IOError:
            print 'Error loading PiMessage daemon in .profile'

        # start the daemon manually this time
        os.system(start_daemon_cmd)

    print 'PiMessage has been successfully installed.'
    exit(0)


def uninstall():
    """Uninstaller for pimessage"""
    # status = os.system('rm -r -f '+data_dir)
    shutil.rmtree(data_dir, ignore_errors=True)

    if status != 0:
        print 'Error in removing ~/.pimessage'

    # Remove daemon from .profile
    try:
        _profile = os.path.join(utils.get_home_dir(), '.profile')
        with open(_profile, 'r') as fname:
            buf = fname.read()

        # process buffer
        lines = buf.split('\n')
        dir_path = os.path.abspath(os.path.dirname(sys.argv[0]))
        daemon_line0 = '#start pimessage daemon'
        daemon_line1 = dir_path+'/pmdaemon.py &'
        daemon_line2 = dir_path+'/pmdaemon.py -f'

        lines_to_append = []
        for line in lines:
            if (line != daemon_line0 and line != daemon_line1 and
                    line != daemon_line2):
                lines_to_append.append(line)

        buf = '\n'.join(lines_to_append)

        with open(_profile, 'w') as fname:
            fname.write(buf)

    except Exception as err:
        print 'Error in handling ~/.profile'
        print '%s' % str(err)
        status = 1

    # Remove pimessage alias from .bashrc
    try:
        _bashrc = os.path.join(utils.get_home_dir(), '.bashrc')
        with open(_bashrc, 'r') as fname:
            buf = fname.read()

        # process buffer
        lines = buf.split('\n')
        alias_line0 = '# For PiMessage -- do not delete'
        alias_line1 = 'alias pimessage='+dir_path+'/pimessage.py'

        lines_to_append = []
        for line in lines:
            if line != alias_line0 and line != alias_line1:
                lines_to_append.append(line)

        buf = '\n'.join(lines_to_append)

        with open(_bashrc, 'w') as fname:
            fname.write(buf)

    except Exception as err:
        print 'Error in handling ~/.bashrc'
        print '%s' % str(err)
        status = 1


    if status != 0:
        print 'Error removing PiMessage.'
    else:
        print 'PiMessage has been successfully uninstalled.'
    return status


def grab_opt(argv, num):
    """returns the nth arg or returns NULL_ARGUMENT"""
    if len(argv) <= num:
        return NULL_ARGUMENT
    else:
        return argv[num]

def parse_opts(argv, edit_cmd):
    """Parse all options and figure out what to do"""
    script_name = argv[0]
    opt2 = grab_opt(argv, 2)
    opt1 = grab_opt(argv, 1)

    if opt1 == NULL_ARGUMENT:
        # only contains the script name, no arguments
        # call usage function
        usage(script_name)
        exit(1)


    if opt1 == '-h' or opt1 == '--help' or opt1 == 'help':
        usage(script_name)
        exit(0)
    elif opt1 == 'ip': # show host IP address
        print host_ip # a global value
    elif opt1 == 'logo':
        # This is a secret option to display the Raspberry Pi ASCII logo
        show_logo()
        exit(0)
    elif opt1 == 'kill':
        # This is a secret option to kill the daemon
        exit(kill_daemon())
    elif opt1 == 'uninstall':
        # This is a secret option to completely remove PiMessage
        status = uninstall()
        exit(status)

    elif opt1 == 'history' or opt1 == 'recent':
        # show recent chat history
        exit(show_recents((opt2 == '-a')))
    elif opt1 == 'new' or opt1 == 'compose': # compose a message
        if opt2 == NULL_ARGUMENT:
            print 'Invalid number of operands for %s option' % opt1
            usage(script_name)
            exit(1)

        opt3 = grab_opt(argv, 3)
        opt4 = grab_opt(argv, 4)

        if opt3 == '-m' and opt4 != NULL_ARGUMENT:
            send_message(opt2, edit_cmd, opt4)
        else:
            send_message(opt2, edit_cmd)

    elif opt1 == 'read': # read a conversation
        if opt2 == NULL_ARGUMENT:
            print 'Invalid number of operands for %s option' % opt1
            usage(script_name)
            exit(1)
        val = read_convo(opt2)
        exit(val)

    elif opt1 == 'rm-convo': # delete a conversation
        if opt2 == NULL_ARGUMENT:
            print 'Invalid number of operands for %s option' % opt1
            usage(script_name)
            exit(1)

        val = rm_convo(opt2)
        exit(val)

    elif opt1 == 'resend': # resend a failed message
        if opt2 == NULL_ARGUMENT:
            print 'Invalid number of operands for %s option' % opt1
            usage(script_name)
            exit(1)

        send_message(opt2, edit_cmd, '', False)


    elif opt1 == 'contacts':
        # contacts of the form:
        # Adam Smith\t1.2.3.4
        # Betty Rogers\t98.76.54.321
        opt3 = grab_opt(argv, 3)
        flag_list = list(opt2) + list(opt3) # parse all characters

        a_flag = False
        o_flag = False
        for flag in flag_list:
            if flag == '-':
                pass
            elif flag == 'a':
                a_flag = True
            elif flag == 'o':
                o_flag = True

        # Display the contact list in less
        ret = 0
        if a_flag and o_flag:
            # stdout, show IP addresses
            try:
                with open(data_dir+'contacts') as fname:
                    sys.stdout.write(fname.read())
            except IOError:
                print 'Unable to open contacts file'
                ret = 2

        elif a_flag:
            # display in less, show IP addresses
            ret = os.system('less '+data_dir+'contacts')
        elif o_flag:
            # stdout, no IP addresses
            try:
                with open(data_dir+'contacts') as fname:
                    names = [line.split('\t')[0] for line in fname.readlines()]
                    print '\n'.join(names)
            except IOError:
                print 'Unable to open contacts list'
                ret = 1
        else:
            # display in less, no IP addresses
            ret = os.system("sed 's/\t.*$//' " + data_dir+'contacts | less')

        exit(ret)


    elif opt1 == 'add':
        opt3 = grab_opt(argv, 3)

        if opt3 == NULL_ARGUMENT:
            print 'Invalid number of operands for %s option' % opt1
            usage(script_name)
            exit(1)

        # default is to NOT overwrite (prompt user if they want to change)
        add_contact(opt2, opt3, 'n')

    elif opt1 == 'force-link':
        # force-link a contact to an IP
        # essentially, just overwrite a contact's IP

        opt3 = grab_opt(argv, 3)

        if opt3 == NULL_ARGUMENT:
            print 'Invalid number of operands for %s option' % opt1
            usage(script_name)
            exit(1)

        # default is to overwrite old contact
        add_contact(opt2, opt3, 'y')

    elif opt1 == 'rm-contact':
        if opt2 == NULL_ARGUMENT:
            print 'Invalid number of operands for %s option' % opt1
            usage(script_name)
            exit(1)

        ret = rm_contact(opt2)
        if ret != 0:
            print 'Error in removing your contact.'
            exit(ret)

        resp = raw_input('Would you also like to delete conversation history '
                         'for this contact? (y/n) ')
        if resp == 'y' or resp == 'yes' or resp == 'Y':
            print 'deleting conversation for', opt2
            ret = rm_convo(opt2)

        exit(ret)

    elif opt1 == 'config':
        opt3 = grab_opt(argv, 3)
        if opt3 == NULL_ARGUMENT:
            print 'Invalid number of operands for %s option' % opt1
            usage(script_name)
            exit(1)

        if opt2 == 'editor':
            if os.system('which '+opt3+' &>/dev/null') == 0:
                with open(data_dir+'editor', 'w') as fname:
                    fname.write(opt3)
            else:
                print 'Error: %s is not a recognized command.' % opt3

        else:
            print 'Unknown variable. Cannot config.'
            exit(1)

    else:
        # some invalid option
        print 'Invalid option %s' % opt1
        usage(script_name)
        exit(1)



########################
##  Option functions  ##
########################

def usage(script_name):
    """
    Prints usage/help information
    This is called by --help, -h, or invalid usage
    """

    # print usage info
    print 'Usage: %s [options] [option arguments]\n' % script_name

    # print help/option info
    # Don't indent on docstring
    print """Options:
help, -h, --help                           help
ip                                         show host IP address
history, recent        [-a]                show recent chat history
compose, new           CONTACT [-m 'msg']  compose & send message
read                   CONTACT             read a conversation
rm-convo               CONTACT             delete a conversation
resend                 CONTACT             resend a failed message
force-link             CONTACT   IP        force-link contact to IP
config                 VARIABLE, VALUE     configure variables
contacts               [-a or -o]          view contact list [with IPs]
add                    CONTACT   IP        add a contact
rm-contact             CONTACT             delete a contact

"""

    return # exit after calling this function


def add_contact(name, ip_addr, overwrite):
    """Search for if this person is already there"""
    with open(data_dir+'contacts', 'r') as fname:
        all_contacts = fname.read()
    contact_idx = all_contacts.find(name+'\t')
    if contact_idx != -1:
        if overwrite != 'y':
            print '%s is already entered in your contact list.' % name
            overwrite = raw_input('Would you like to overwrite this entry? '
                                  '(y/n) ')
        if overwrite != 'y':
            print 'Not overwriting the entry. Terminating.'
            exit(1)
        else:
            # remove the old one
            rm_contact(name)
            print 'Your contact has been updated.'


    # add contact normally
    add_string = name+'\t'+ip_addr+'\n'
    with open(data_dir+'contacts', 'a') as fname:
        fname.write(add_string)

    # use GNU sort
    sort_cmd = 'sort -f '+data_dir+'contacts > '+data_dir+'sort_contacts'
    os.system(sort_cmd)

    # overwrite old file
    os.system('mv '+data_dir+'sort_contacts '+data_dir+'contacts')

    return 0

def rm_contact(name):
    """Delete someone from your contacts"""
    with open(data_dir+'contacts', 'r') as fname:
        all_contacts = fname.read()

    # this is the part up until that contact
    contact_idx = all_contacts.find(name+'\t')
    if contact_idx == -1:
        # contact isn't in here
        return 1

    first_half = all_contacts[0:contact_idx]

    # this is the part right after that contact until the end
    second_half = ip.string_slice(all_contacts, name)
    second_half = ip.string_slice(second_half, '\n')
    second_half = second_half[1:]
    all_contacts = first_half + second_half

    with open(data_dir+'contacts', 'w') as fname:
        fname.write(all_contacts) # add the new entry later

    return 0


def show_logo():
    """Shows the logo"""
    print r"""
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
    return

def kill_daemon():
    """
    This will kill the PiMessage daemon
    Note: this is NOT recommended for normal use
    """
    return os.system(os.path.dirname(sys.argv[0]) + '/killDaemon')

def show_recents(is_all):
    """
    This shows the 10 most recent conversations & the top message in each
    one by default. This has the option to show all recent conversations in
    a similar fashion if `is_all' is True.
    """

    # Build the list of recent conversations
    get_convo_cmd = 'ls -t '+data_dir+'conversations/'
    sorted_convos = subprocess.Popen(get_convo_cmd.split(),
                                     stdout=subprocess.PIPE).communicate()[0]

    convo_list = sorted_convos.split('\n')

    if not is_all:
        convo_list = convo_list[0:9]

    for k in convo_list:
        # remove .conv from each conversation
        vals = k.split('.')
        if len(vals) == 2:
            k = vals[0]
        else:
            k = '.'.join(vals[0:len(vals)-1])

        print k

    return

def read_convo(my_contact):
    """
    Read the saved conversation with this contact if one exists
    Display a message to indicate if no conversation exists
    """

    conv_file = data_dir+'conversations/'+my_contact+'.conv'

    try:
        # If file can't be read, than we should return immediately
        with open(conv_file, 'r'):
            pass
    except IOError:
        print("It appears that you don't currently have a conversation with",
              my_contact)
        return 0

    return os.system('less '+conv_file)

def rm_convo(my_contact):
    """
    Delete the conversation for this contact
    Display a message to indicate if no conversation exists
    """

    conv_file = data_dir+'conversations/'+my_contact+'.conv'

    try:
        # If file can't be read, than we should return immediately
        with open(conv_file, 'r'):
            pass
    except IOError:
        print 'No conversation for', my_contact, 'could be found.'
        return 1

    return os.system('rm '+conv_file)

def send_message(my_contact, editor, text='', should_compose=True):
    """
    Sends a message to 'my_contact'
    Uses 'editor' to compose the message unless 'text' is not empty
    """

    # fetch sender IP
    #if host_ip == IP_FAILURE:
    #    exit(1)

    # fetch recipient IP

    with open(data_dir+'contacts') as fname:
        for line in fname:
            rec = line.split('\t')
            if rec[0] == my_contact:
                rec_ip = rec[1].rstrip('\n')
                break

    ## Compose the message

    # store this in conversations directory
    file_name = data_dir+'conversations/msg'+my_contact

    if should_compose:
        if not text:
            if os.system(editor+' '+file_name):
                print 'Error in opening message file.'
                exit(2)
        else:
            # use the short message typed by the user at the prompt
            try:
                with open(file_name, 'w') as fname:
                    fname.write(text)
            except IOError:
                print 'Error composing your file on disc.'
                exit(1)
    else:
        # check to see if a saved message actually exists
        try:
            with open(file_name, 'r'):
                pass
        except IOError:
            # if we couldn't open the file, then we can't resend it
            print 'Unable to find a saved message for %s' % my_contact
            exit(1)


    # prompt if they want to send or not
    should_send = raw_input('To send or not to send; that is the question '
                            '(y/n): ')

    if (should_send != 'y' and should_send != 'Y' and should_send != 'yes' and
            should_send != 'Yes' and should_send != 'YES'):
        print('Your message has been saved for next time you compose a message '
              'to %s' % my_contact)
        exit(5)

    # get time stamp in proper format
    send_time = str(time.time())

    # format the message with the meta data
    msg_lines = [rec_ip, host_ip, send_time, '']

    # msg_lines.append(rec_ip)
    # msg_lines.append(host_ip)
    # msg_lines.append(send_time) # guaranteed two consecutive newlines
    # msg_lines.append('')

    with open(file_name) as fname:
        for line in fname:
            msg_lines.append(line.rstrip('\n'))
    msg_lines.append('')

    msg_text = '\n'.join(msg_lines)

    # Send the full message

    if host_ip != IP_FAILURE:
        sock = socket.socket()
        # host = socket.gethostname()
        try:
            sock.connect((rec_ip, ip.PORT_NUM))
        except socket.error:
            print('Error: Unable to send message. Perhaps you have an '
                  'incorrect IP address?')
            exit(4)

        try:
            sock.sendall(msg_text)

            amount_received = 0
            amount_expected = len(msg_text)
            packets = []

            while amount_received < amount_expected:
                data = sock.recv(16)
                amount_received += len(data)
                packets.append(data)

        finally:
            sock.close()   # Close the socket when done
            recv_msg = ''.join(packets)

            if msg_text != recv_msg:
                print 'There may be an error with the data sent'

        # add the message to conversation history
        if utils.save_msg(msg_text, 'send') == utils.TUPLE_FAIL:
            print 'failure in saving your message.'

        # clean up by removing old message to contact
        if os.system('rm '+file_name):
            print 'Error in removing message file.'
            exit(2)
    else:
        print 'Please connect to a network to send your message.'


    return 0

########################
##   Main function    ##
########################

def main(argv):
    """Main function"""

    ## Get user information ##
    global op_system
    op_system = os.name
    if op_system != 'nt':
        op_system = subprocess.Popen(['uname', '-s'],
                                     stdout=subprocess.PIPE).communicate()[0]
        op_system = op_system.rstrip('\n')
        # change Cygwin to say 'CYGWIN' always
        under_score_idx = op_system.find('_')
        if under_score_idx != -1:
            op_system = op_system[:under_score_idx]

    if op_system != 'Linux' and op_system != 'Darwin':
        print('Error: %s is not a supported operating system at this time.'
              % op_system)
        exit(5)

    global data_dir
    data_dir = os.path.join(utils.get_home_dir(), '.pimessage/')

    opt1 = grab_opt(argv, 1)
    if opt1 == 'uninstall':
        exit(uninstall())

    script_name = argv[0]
    dir_exists_cmd = 'test -d ' + data_dir
    if os.system(dir_exists_cmd) != 0:
        install(script_name, data_dir)

    dir_files = subprocess.Popen(['ls', '-A', data_dir],
                                 stdout=subprocess.PIPE).communicate()[0]

    # must be in correct ls -A order
    correct_dir_files = """contacts
conversations
daemonError.log
editor
"""

    alt_dir_files = """contacts
conversations
editor
"""

    if dir_files != correct_dir_files and dir_files != alt_dir_files:
        install(script_name, data_dir)

    # get user's chosen editor
    edit_cmd = open(data_dir+'editor', 'r').read().rstrip('\n')
    if not subprocess.Popen(['which', edit_cmd],
                            stdout=subprocess.PIPE).communicate()[0]:
        print('Error: %s is not a valid editor. Please adjust your editor '
              'value' % edit_cmd)
        exit(2)

    global host_ip
    host_ip = ip.get_host_ip()
    #if host_ip == IP_FAILURE:
    #    print 'Error: your IP address could not be correctly retrieved.'
    #    exit(2)

    ## Option parsing ##
    # figure out which option was called
    parse_opts(argv, edit_cmd)
    return 0


if __name__ == '__main__':
    STATUS = main(sys.argv)
    exit(STATUS)

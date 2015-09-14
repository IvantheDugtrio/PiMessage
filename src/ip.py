#!/usr/bin/python

"""
Methods related to handling ip addresses
"""

import subprocess
import re

IP_FAILURE = 1
PORT_NUM = 16246

def string_slice(input_str, search_str):
    """
    slices the input string so that the search_str is the beginning of the
    returned string.  So if you pass in 'hello world' as the first string
    and then 'lo' as the second string, this function will return "lo
    world'. If you pass in 'foo" as the second string instead, you will get
    the empty string returned. If you pass in 'h' as the first string, you
    will get 'hello world' as the output.
    """

    search_sub = input_str.find(search_str)
    if search_sub == -1:
        returner = ''
    else:
        returner = input_str[search_sub:]
    return returner

def get_host_ip():
    """
    Returns the user's WLAN or LAN ip address if connected to a network
    Returns IP_FAILURE if no address was found
    """

    ipaddress = IP_FAILURE # default case
    cmd_output = subprocess.Popen('ifconfig',
                                  stdout=subprocess.PIPE).communicate()[0]


    ## slice the cmd_output string:
    mod_output = string_slice(cmd_output, 'wlan0')
    if mod_output == '':
        mod_output = string_slice(cmd_output, 'eth0')
        if mod_output == '':
            return IP_FAILURE

    mod_output = string_slice(mod_output, 'inet')
    if mod_output == '':
        return IP_FAILURE

    # slice the cmd_output string:
    mod_output = string_slice(mod_output, ':')
    if mod_output == '':
        return IP_FAILURE

    ## perhaps there is a good way to clean this up? ##
    match_object = re.search(r'\d', mod_output)
    if match_object: # it returned a match
        start_sub = match_object.start()
    else:
        return IP_FAILURE

    match_object = re.search(' ', mod_output)
    if match_object: # it returned a match
        end_sub = match_object.start()
    else:
        return IP_FAILURE

    ipaddress = mod_output[start_sub:end_sub]
    # ipcmd = 'wget -qO- icanhazip.com'
    # ipaddress = subprocess.Popen(ipcmd.split(),
    #                              stdout=subprocess.PIPE).communicate()[0]

    # ipaddress = ipaddress.rstrip()


    return ipaddress # default is IP_FAILURE

#!/usr/bin/env python

from marmoset import Marmoset
from getpass import getpass
import os
import glob
import sys


# monkey-patch SSL because verification fails on 2.7.9
if sys.hexversion == 34015728:
    import ssl
    if hasattr(ssl, '_create_unverified_context'):
        ssl._create_default_https_context = ssl._create_unverified_context

username = raw_input('Username: ')
password = getpass('Password: ')

m = Marmoset(username, password)

def getParams(path):
    """Get a list of parameters by searching the file."""
    f = open(path)
    for line in f:
        if line.startswith(';;;(autosubmit'):
            params = line.split(' ', 2)
            if len(params) != 3: return

            params.pop(0)
            params[1] = params[1].rstrip(')\n')

            f.close()

            return params

    f.close()
    return False

def getFiles(filetype):
    """Get all the files of the specified type from the cwd"""
    cwd = os.getcwd()
    return glob.glob(cwd + '/*.' + filetype)

def submitAllFiles():
    """Submit all valid files in the cwd"""
    fileList = getFiles('rkt')
    paramsMap = map(lambda f: (getParams(f), f), fileList)
    #return paramsMap
    for fileParams in paramsMap:
        m.submit(fileParams[0][0], fileParams[0][1], fileParams[1])


submitAllFiles()
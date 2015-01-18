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

RACKET_KEYWORD = ';;;!'
C_KEYWORD = '///'
LINE_SEARCH_LIMIT = 10
langLookup = {'.rkt' : RACKET_KEYWORD, '.c' : C_KEYWORD}

username = raw_input('Username: ')
password = getpass('Password: ')

m = Marmoset(username, password)

class MarmosetAssignment:
    """Stores one marmoset assignment problem and a list of its files"""

    def __init__(self, course='', assignment='', files=[]):
        self.course = course
        self.assignment = assignment
        self.files = files


    def setCourse(self, course):
        self.course = course

    def setAssignment(self, assignment):
        self.assignment = assignment

    def addFile(self, f):
        self.files.append(f)

    def submit(self, m):
        m.submit(self.course, self.assignment, self.files)



def getParamsFromFile(path):
    """
    Get a list of parameters by searching the file.

    param path: Path to the file (string)
    returns: A list of parameters [course, assignment]
    """
    f = open(path)
    fileType = os.path.splitext(path)[1]
    keyword = langLookup[fileType]

    for line in f:
        if line.startswith(keyword):
            params = line.split(' ', 2)
            if len(params) != 3: return False

            params.pop(0)
            params[1] = params[1].rstrip(')\n')

            f.close()

            return params

    f.close()
    return False

def getFilePaths(filetype):
    """
    Get all the files of the specified type from the cwd.

    param filetype: The filetype to search for
    returns: A list of file paths
    """
    cwd = os.getcwd()
    return glob.glob(cwd + '/*' + filetype)

def getAllParams(files):
    """
    Get all parameters from the list of files.

    param files: A list of files
    returns: a list of MarmosetAssignments
    """
    marmoProblems = dict()
    fileList = []
    for filetype in langLookup:
        fileList += getFilePaths(filetype)

    paramsMap = zip(fileList, map(lambda f: getParamsFromFile(f), fileList))

    validFiles = (x for x in paramsMap if x[1] != False)
    for entry in validFiles:
        course = entry[1][0]
        assignment = entry[1][1]
        fileName = entry[0] # FIXME: Breaks when there are spaces in path
        id = course + assignment # 'course' + 'assgignment'
        if id in marmoProblems:
            # add filename to existing MarmosetAssignment
            marmoProblems[id].addFile(fileName)
        else:
            marmoProblems[id] = MarmosetAssignment(course, assignment)
            marmoProblems[id].addFile(fileName)

    return marmoProblems.values()

def submitAll(marmosetAssignments, m):
    for problem in marmosetAssignments:
        problem.submit(m)

submitAll(getAllParams(2), m)
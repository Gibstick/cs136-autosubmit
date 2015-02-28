#!/usr/bin/env python
from __future__ import print_function
from marmoset import Marmoset
from getpass import getpass
import os
import glob
import sys
import threading
import fileinput
import ntpath
# Hack to make print "thread safe"
print = lambda x: sys.stdout.write("%s\n" % x)

# monkey-patch SSL because verification fails on 2.7.9
if sys.hexversion == 34015728:
    import ssl

    if hasattr(ssl, '_create_unverified_context'):
        # noinspection PyProtectedMember
        ssl._create_default_https_context = ssl._create_unverified_context


RACKET_KEYWORD = ';;;!'
C_KEYWORD = '///!'
LINE_SEARCH_LIMIT = 10
langLookup = {'.rkt': RACKET_KEYWORD, '.c': C_KEYWORD, '.h': C_KEYWORD}
MAX_DEPTH = 2

m_username = raw_input('Username: ')
m_password = getpass('Password: ')


class MarmosetAssignment:
    """
    Stores one marmoset assignment problem and a list of its files.

    """

    def __init__(self, course='', assignment=''):
        """
        Construct with course and assignment.

        :param course:
        :type course: str
        :param assignment:
        :type assignment: str

        :return: An assignment instance
        :rtype: MarmosetAssignment
        """
        self.course = course
        self.assignment = assignment
        self.files = []

    def set_course(self, course):
        """
        Setter for the instance field "course"

        :param course:
        :type course: str

        :return: None
        """
        self.course = course

    def set_assignment(self, assignment):
        """
        Setter for the instance field "assignment"

        :param assignment:
        :type assignment: str

        :return: None
        """
        self.assignment = assignment

    def add_file(self, f):
        """
        Add a file to the instance's list of files

        :param f: A path
        :type f: str

        :return: None
        """
        self.files.append(f)

    def submit(self, username, password):
        """
        Submit all files in the instance's files field.

        :param username: CAS username
        :type username: str
        :param password: CAS password
        :type password: str

        :return: None
        """
        marmoset = Marmoset(username, password)
        #Marmoset.login(marmoset, username, password) # Temporary fix for marmoste 1.1.3 regression

        if len(self.files) == 1:
            self.files = self.files[0]  # Fix for zipping the entire directory structure

        print("Submitting {} {} ".format(self.course, self.assignment))
        result = marmoset.submit(self.course, self.assignment, self.files)
        if result:
            print("Success!")
        else:
            print("Submission failed (check login credentials)")

    def async_submit(self, username, password):
        """
        Submit all files in the instance's files field without blocking.

        :param username: CAS username
        :type username: str
        :param password: CAS password
        :type password: str

        :return: None
        """

        for i in range(len(self.files)):
            t = threading.Thread(target=self.submit, args=(username, password, ))
            t.start()


def get_params_from_file(path):
    """
    Get a list of parameters by searching the file.

    :param path: Path to the file
    :type path: str

    :return: A list of parameters [course, assignment]
    :rtype: list
    """
    f = fileinput.input(path)
    file_extension = os.path.splitext(path)[1]
    keyword = langLookup[file_extension]

    for line in f:
        if f.lineno() >= 10:  # limit of 10 lines
            break

        if line.startswith(keyword):
            params = line.split(' ', 2)
            if len(params) != 3:
                return False

            params.pop(0)
            params[1] = params[1].rstrip(')\n')

            f.close()

            return params

    f.close()
    return False


def get_file_paths(file_extension):
    """
    Get all the files of the specified type from the cwd.

    :param file_extension: The file type to search for
    :type file_extension: str

    :return: A list of file paths
    :rtype: list
    """
    cwd = os.getcwd()
    return glob.glob(os.path.join(cwd, '*' + file_extension))


def get_file_paths_recursive(file_extension, path='.', depth=0):
    """
    Get all the files of the specified type from the cwd recursively
    up to three levels of nesting.

    :param file_extension: The file type to search for
    :type file_extension: str

    :return: A list of file paths
    :rtype: list
    """
    file_paths = []
    for (dirpath, dirnames, filenames) in os.walk(path):
        if depth <= MAX_DEPTH:
            for subdir in dirnames:
                file_paths.extend(
                    get_file_paths_recursive(file_extension,
                                             os.path.join(dirpath, subdir),
                                             depth + 1)
                )
        for filename in filenames:
            if filename.endswith(file_extension) and not os.path.islink(filename):
                file_paths.append(os.path.join(dirpath, filename))
        break

    return file_paths


def get_all_params(file_list):
    """
    Get all parameters from the list of files.


    :param file_list: A list of file paths
    :type file_list: list
    :return: A list of MarmosetAssignments
    :rtype: list
    """
    marmo_problems = {}
    params_map = zip(file_list, map(lambda f: get_params_from_file(f), file_list))

    valid_files = (x for x in params_map if x[1] is not False)
    for entry in valid_files:
        course = entry[1][0]
        assignment = entry[1][1]
        filename = entry[0]  # FIXME: Zip behaviour is wonky for absolute paths
        key = (course, assignment)  # 'course' + 'assignment'
        if key in marmo_problems:
            # add filename to existing MarmosetAssignment
            marmo_problems[key].add_file(filename)
        else:
            marmo_problems[key] = MarmosetAssignment(course, assignment)
            marmo_problems[key].add_file(filename)

    return marmo_problems.values()


def submit_all(assignments, username, password):
    for problem in assignments:
        problem.async_submit(username, password)


files = []
for file_exts in langLookup:
    files += get_file_paths_recursive(file_exts)

submit_all(get_all_params(files), m_username, m_password)


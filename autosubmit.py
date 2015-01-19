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
        # noinspection PyProtectedMember
        ssl._create_default_https_context = ssl._create_unverified_context

RACKET_KEYWORD = ';;;!'
C_KEYWORD = '///'
LINE_SEARCH_LIMIT = 10
langLookup = {'.rkt': RACKET_KEYWORD, '.c': C_KEYWORD}

username = raw_input('Username: ')
password = getpass('Password: ')

m = Marmoset(username, password)


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

    def submit(self, marmoset):
        """
        Submit all files in the instance's files field.

        :param marmoset: Marmoset instance
        :type marmoset: Marmoset

        :return: None
        """
        if len(self.files) == 1:
            self.files = self.files[0]  # Fix for zipping the entire directory structure

        print("Submitting " + self.course + " " + self.assignment)
        marmoset.submit(self.course, self.assignment, self.files)


def get_params_from_file(path):
    """
    Get a list of parameters by searching the file.

    :param path: Path to the file
    :type path: str

    :return: A list of parameters [course, assignment]
    :rtype: list
    """
    f = open(path)
    file_extension = os.path.splitext(path)[1]
    keyword = langLookup[file_extension]

    for line in f:
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
    :rtype: str
    """
    cwd = os.getcwd()
    return glob.glob(cwd + '/*' + file_extension)


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
        filename = os.path.basename(entry[0])  # FIXME: Zip behaviour is weird
        key = (course, assignment)  # 'course' + 'assignment'
        if key in marmo_problems:
            # add filename to existing MarmosetAssignment
            marmo_problems[key].add_file(filename)
        else:
            marmo_problems[key] = MarmosetAssignment(course, assignment)
            marmo_problems[key].add_file(filename)

    return marmo_problems.values()


def submit_all(assignments, marmoset):
    for problem in assignments:
        problem.submit(marmoset)


files = []
for file_exts in langLookup:
    files += get_file_paths(file_exts)

submit_all(get_all_params(files), m)

# Return.py
# This class represents return values from lox functions.
# Written by Joel Peckham.
# Last Modified: 2020-03-18.

class Return(Exception):
    def __init__(self, value: object):
        self.value = value
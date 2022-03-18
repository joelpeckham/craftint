# test.py
# This utility runs all the lox files in the testCode directory first with jlox and the with pylox.
# It then compares the output of each to see if they are the same.
# Written by: Joel Peckham.
# Last Modified: 2022-03-18

import os, sys, subprocess

# Assume the testCode directory is in the same directory as this file.
thisDir = os.path.dirname(os.path.realpath(__file__))
testDir = os.path.join(thisDir, "testCode")

JLOX_PATH = "/Users/joel/Documents/School/OPL/craftint/jlox"
PYLOX_PATH = "/Users/joel/Documents/School/OPL/craftint/pylox"

categories = [(cat, [os.path.join(os.path.join(testDir, cat),fileName) for fileName in os.listdir(os.path.join(testDir, cat))]) for cat in os.listdir(testDir)]

for category, filePaths in categories:
    for filePath in filePaths:
        # Run the file with jlox.
        result = subprocess.run([JLOX_PATH, filePath], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        jloxOutput = result.stdout.decode("utf-8")
        jloxErrors = result.stderr.decode("utf-8")
        # Run the file with pylox.
        result = subprocess.run([PYLOX_PATH, filePath], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        pyloxOutput = result.stdout.decode("utf-8")
        pyloxErrors = result.stderr.decode("utf-8")
        # Compare the outputs.
        if jloxOutput != pyloxOutput:
            fileName = os.path.basename(filePath)
            print( "Test failed: " + fileName + " in " + category + ".")
            print( "Jlox: " + jloxOutput)
            print( "Pylox: " + pyloxOutput)
            print( "Jlox Errors: " + jloxErrors)
            print( "Pylox Errors: " + pyloxErrors)
            print( "")
        else:
            print( "Test passed: " + fileName + " in " + category + ".")